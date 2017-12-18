import os
import sys
import urllib
import paramiko
from . import apt, remote
from celery import shared_task
from core import confirm
import logging
log = logging.getLogger(__name__)


@shared_task
def install_pkg(pkg_name):
    from subprocess import Popen
    import platform
    # import subprocess

    # check if we are root
    # if os.geteuid() != 0:
    #     raise ValueError("Need to be root to install packages")

    if 'Linux' == platform.system():
        # platform.linux_distribution() deprecated in 3.7

        # Arch
        pacman = '/usr/bin/pacman'
        if os.path.isfile(pacman):
            p = Popen(['sudo', '-S', pacman, '-S', '--noconfirm', pkg_name])
            p.communicate()
            p.wait()
            # sudo_prompt = p.communicate(sudo_password + '\n')[1]
        else:
            raise NotImplementedError(
                "don't know how to install packages in this Linux")

    elif 'Windows' == platform.system():
        raise NotImplementedError(
            "don't know how to install packages in Windows")
    else:
        raise NotImplementedError(
            "don't know how to install packages in Unknown")


def service_is_running(service):
    # systemctl is-active sshd
    from subprocess import Popen
    exit_code = Popen(['systemctl', '-q', 'is-active', service]).wait()
    return exit_code == 0


def configure_docker():
    import docker
    cli = docker.from_env()
    try:
        cli.images.get('ubuntu:17.04')
    except Exception:
        print('Getting Ubuntu image...')
        cli.images.pull('ubuntu:17.04')

    try:
        cli.images.get('postgres:latest')
    except Exception:
        print('Getting Postgres image...')
        cli.images.pull('postgres:latest')

    print(os.getcwd())
    cli.images.build(path='../docker/', tag='pashinin.com')
    # container = cli.containers.run('pashinin.com',
    #                                detach=True)

    print(cli.containers.list())
    print(cli.images.list())


def install(program):
    from shutil import which
    from subprocess import Popen
    if which(program) is not None:

        if program == 'docker':
            if service_is_running('docker'):
                print('Docker is running')
            else:
                print('starting Docker...')
                p = Popen(['sudo', '-S', 'systemctl', 'start', 'docker'])
                p.communicate()
                p.wait()

            # check docker images
            try:
                import docker
                docker.from_env()
            except Exception:
                print('Installing docker via pip')
                p = Popen(['sudo', 'pip', 'install', 'docker'])
                p.communicate()
                p.wait()

            # if permission denied - add user to "docker" group
            try:
                import docker
                client = docker.from_env()
                client.containers.list()
            except Exception as e:
                print(e)
                # gpasswd -a user docker
                import getpass
                p = Popen(['sudo', 'gpasswd', '-a', getpass.getuser(),
                           'docker'])
                p.communicate()
                p.wait()
                msg = """You were added to group "docker".
Please restart! Logout and login may not help!"""
                print('*'*len(msg))
                print(msg)
                print('*'*len(msg))
                raise ValueError("Restart!")

            configure_docker()

        return

    import platform

    pkgs = {
        'flake8': {
            'ubuntu': 'python-flake8',
            'arch': 'flake8',
        },
        'docker': {
            # 'ubuntu': 'python-flake8',
            'arch': 'docker',
        },
        'docker-compose': {
            # 'ubuntu': 'python-flake8',
            'arch': 'docker-compose',
        },
    }
    if program in pkgs:
        if 'Linux' == platform.system():
            # platform.linux_distribution() deprecated in 3.7

            # Arch
            if os.path.isfile('/usr/bin/pacman'):
                install_pkg(pkgs[program]['arch'])
            else:
                raise NotImplementedError(
                    "don't know how to install {} in this Linux"
                    .format(program))

        elif 'Windows' == platform.system():
            raise NotImplementedError(
                "don't know how to install packages in Windows")
        else:
            raise NotImplementedError(
                "don't know how to install packages in Unknown")
    else:
        raise ValueError("Don't know how to install {}".format(program))


# class Program(object):
#     name = None
#     host = 'localhost'

#     def __init__(self, name, host='localhost'):
#         self.name = name
#         self.host = host

#     def install(self):
#         raise NotImplementedError(f'How to install {self.name}?')


# class ElasticSearch(object):
#     name = 'ElasticSearch'

#     def install(self):
#         pass


@shared_task
def install_ElasticSearch(host=None):
    # TODO:
    # change bind addresses in config:
    # network.host: ["localhost", "10.254.239.2"]
    tty = sys.stdout.isatty()
    url = 'https://artifacts.elastic.co/downloads/' \
          'elasticsearch/elasticsearch-6.0.1.deb'
    sha = 'fa92bf63d32712dc166ab7c21e460cb6b424d4b8ae839a0fe0c8ee6167b981c' \
          'e53902f51088cbdbc9ae8fc0e31e621e3dfa878de0b88e11f7a23aea13e6d6fa3'  # noqa
    if apt.installed('elasticsearch', host=host):
        if host:
            print(f'ElasticSearch is already installed on {host}.')
        else:
            print(f'ElasticSearch is already installed on this machine.')
    elif not tty or confirm(f'Install ElasticSearch on {host}?'):
        if host:
            print(f'Installing ElasticSearch on {host}...')
            apt.install_from_url(url, host)
            # raise NotImplementedError('another host')
        else:
            print(f'Installing ElasticSearch locally...')

            f = '/tmp/es.deb'
            if not os.path.isfile(f):
                urllib.request.urlretrieve(url, f)
            else:
                file_size = os.path.getsize(f)
                print(f'{f} exists ({file_size})')
                # TODO: install deb file

                # cache = apt.Cache()
                # if cache['package-name'].is_installed:
                if apt.installed('elasticsearch', host=host):
                    print(f"installed on {host}")
                else:
                    print("NO it's NOT installed")
                    apt.install(f)


def get_java_version(host=None):
    return None


@shared_task
def install_java8(host=None):
    c = remote.create_connection(host)
    res = remote.get_output(
        'java -version',
        host=host,
        c=c
    )
    java_installed = 'command not found' not in res['err']
    version_string = res['err'].split('\n')[0]

    # version string start with either
    # "openjdk" or "java"
    oracle = version_string.startswith('java')
    openjdk = not oracle
    print(version_string)
    if oracle:
        print('ORACLE')
    # print('out:', out)
    # print('err:', err)
    # echo debconf shared/accepted-oracle-license-v1-1 select true | \
    #     sudo debconf-set-selections
    # $ echo debconf shared/accepted-oracle-license-v1-1 seen true | \
    #     sudo debconf-set-selections

    if not java_installed or openjdk:
        apt.ppa('webupd8team/java', host=host)
        remote.get_output(
            'echo debconf shared/accepted-oracle-license-v1-1 select true '
            '|  sudo debconf-set-selections',
            host=host,
            c=c
        )
        remote.get_output(
            'echo debconf shared/accepted-oracle-license-v1-1 seen true '
            '| sudo debconf-set-selections',
            host=host,
            c=c
        )
        apt.install('oracle-java8-installer', host=host, c=c)
    # apt.install('vim', host=host, c=c)


def install_xpack():
    """X-Pack is an Elastic Stack extension.

    It bundles security, alerting, monitoring, reporting, machine
    learning, and graph capabilities into one easy-to-install package.

    """
    pass


def install_Metricbeat(host=None):
    url = 'https://artifacts.elastic.co/downloads/beats/' \
          'metricbeat/metricbeat-6.1.0-amd64.deb'
    apt.install_from_url(url, host)
    # TODO: enable in systemd
    # TODO: start


@shared_task
def install_grafana(host=None):
    # TODO: enable in systemd (disabled by default)
    pass


@shared_task
def install_Logstash(host=None):
    tty = sys.stdout.isatty()
    url = 'https://artifacts.elastic.co/downloads/logstash/logstash-6.1.0.deb'
    sha = 'fa92bf63d32712dc166ab7c21e460cb6b424d4b8ae839a0fe0c8ee6167b981c' \
          'e53902f51088cbdbc9ae8fc0e31e621e3dfa878de0b88e11f7a23aea13e6d6fa3'  # noqa

    install_java8(host=host)
    apt.install_from_url(url, host)

    # TODO
    # Before starting - create configs files or get an error:
    # No config files found in path {:path=>"/etc/logstash/conf.d/*.conf"}
    # /etc/logstash/conf.d/logstash-simple.conf

    # sudo usermod -a -G adm logstash
    # Or error: failed to open /var/log/syslog: Permission denied
    # add_user_to_group('logstash', 'adm', host=host)

    # TODO:
    # enable service
    # run service


@shared_task
def install_project_locally():
    # import pip
    # pip.main(['install', 'python-distutils-extra'])
    # pip.main(['install', 'python-apt'])

    hosts_all = (
        '10.254.239.1',
        '10.254.239.2',
        '10.254.239.3',
        '10.254.239.4',
    )

    # prepare:
    # ve
    # requirements
    #
    tty = sys.stdout.isatty()

    # ES
    for host in [
            '10.254.239.2',
            '10.254.239.3',
    ]:
        install_java8(host=host)
        install_ElasticSearch(host=host)

    # ElasticSearch
    # install_ElasticSearch()
    # install_ElasticSearch(host="10.254.239.3")
    host = "10.254.239.3"
    # install_Logstash(host=host)

    for host in hosts_all:
        install_Metricbeat(host=host)
