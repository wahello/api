/* global alert, fetch, moment, getCookie */

window.urlParams = () => {
  const res = {};
  const query = window.location.search.substring(1);
  const vars = query.split('&');
  for (let i = 0; i < vars.length; i += 1) {
    const pair = vars[i].split('=');
    const [key, value] = pair;
    res[decodeURIComponent(key)] = value;
  }
  return res;
};

// ?a=1&b=2
// getURLParameter('a') == 1;
window.getURLParameter = name => decodeURIComponent((new RegExp(`[?|&]${name}=([^&;]+?)(&|#|;|$)`).exec(window.location.search) || [null, ''])[1].replace(/\+/g, '%20')) || null;

// 3 following blocks are taken from django's docs to fix csrf errors
// https://docs.djangoproject.com/en/dev/ref/csrf/
// https://learn.javascript.ru/cookie#%D1%84%D1%83%D0%BD%D0%BA%D1%86%D0%B8%D1%8F-getcookie-name
window.getCookie = (name) => {
  const matches = document.cookie.match(new RegExp(`(?:^|; )${name.replace(/([.$?*|{}()[\]\\/+^])/g, '\\$1')}=([^;]*)`));
  return matches ? decodeURIComponent(matches[1]) : undefined;
};

// these HTTP methods do not require CSRF protection
window.csrfSafeMethod = method => (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
// $.ajaxSetup({
//     beforeSend: function(xhr, settings) {
//         if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
//             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
//         }
//     }
// });

/* exported showFormErrors */
window.showFormErrors = (errors, form, showtext = false) => {
  // `errors' - a dictionary like {formfield1: ["error1", "error2"], ...}
  Array.from(form.querySelectorAll('[class^=ERR]')).forEach((el) => {
    el.parentNode.removeChild(el);
  });

  // fields errors
  // for (let field in errors) {
  Object.keys(errors).forEach((field) => {
    const msgs = errors[field];
    const msg0 = msgs[0];
    const input = form.querySelector(`[name=${field}]`);
    const cls = `ERR${field}`;
    let msg = form.querySelector(`div.${cls}`);
    if (!msg) {
      msg = document.createElement('div');
      msg.className = cls;
      msg.style.color = '#f96430';
      msg.style.textAlign = 'left';
      msg.style.fontSize = '0.7rem';
    }
    msg.innerHTML = '';
    msg.appendChild(document.createTextNode(msg0));
    if (input) {
      input.classList.add('error');
      if (showtext) {
        input.parentNode.insertBefore(msg, input);
      }
    }
  });

  // form errors
  // special field "__all__"
  // const formErrors = errors['__all__'];
  // if (formErrors) {
  //   Object.keys(formErrors).forEach((key) => {
  //     alert(formErrors[key]);
  //   });
  // }
};

{
  const ready = () => {
    // const $ = document.querySelector.bind(document);
    const $$ = document.querySelectorAll.bind(document);

    // Moment.js
    if (typeof moment === 'function') {
      moment.locale('ru');
      const updateTime = () => {
        // const newYork = moment.tz("America/New_York").format('HH:mm a');
        Array.from($$('time')).forEach((time) => {
          const t = time;
          t.innerHTML = moment(time.getAttribute('datetime')).fromNow();
        });
      };
      // moment.tz.add('America/New_York|EST EDT|50 40|0101|1Lz50 1zb0 Op0');
      updateTime();
      setInterval(() => {
        updateTime();
      }, 30000);
    }

    // Button "Profile" click
    const profile = document.getElementById('profile');
    if (profile) {
      profile.addEventListener('click', (e) => {
        document.getElementById('profile').classList.toggle('pressed');
        document.getElementById('loginbox').classList.toggle('hide');
        e.stopPropagation();
        e.preventDefault();
      });
    }

    if (document.getElementById('siteSwitch')) {
      document.getElementById('siteSwitch').addEventListener('click', (e) => {
        document.getElementById('siteSwitch').classList.toggle('pressed');
        document.getElementById('siteSwitch_menu').classList.toggle('hide');
        e.stopPropagation();
        e.preventDefault();
      });
    }

    // hide any menu when clicked somewhere but not in menu
    document.addEventListener('click', (e) => {
      // if (!closest(e.target, '.popup')) {
      if (!e.target.closest('.popup')) {
        if (document.getElementById('profile')) {
          document.getElementById('profile').classList.remove('pressed');
        }
        if (document.getElementById('siteSwitch')) {
          document.getElementById('siteSwitch').classList.remove('pressed');
        }

        Array.from(document.getElementsByClassName('popup')).forEach((el) => {
          el.classList.add('hide');
        });
      }
    });

    const exit = document.getElementById('exit');
    if (exit) {
      exit.addEventListener('click', (e) => {
        e.preventDefault();
        fetch(e.target.getAttribute('href'), {
          method: 'POST',
          credentials: 'same-origin',
          headers: {
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: '',
        })
        // .then(r => r.json())
          .then(() => {
            window.location.reload();
          });
      });
    }
  };

  if (document.readyState === 'complete' || document.readyState !== 'loading') {
    ready();
  } else {
    document.addEventListener('DOMContentLoaded', ready);
  }
}
