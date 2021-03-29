'use strict';
window.addEventListener('load', function() {

  var signoutvalue = document.getElementById('sign-out').getAttribute('soutvalue');
  if (signoutvalue = true) {
    ;
    setTimeout(function() {
      document.getElementById('sign-out').click();
    }, 500);
  }

  document.getElementById('sign-out').onclick = function() {
    // ask firebase to sign out the use
    firebase.auth().signOut();
  };
  var uiConfig = {
    signInSuccessUrl: '/',
    signInOptions: [
      firebase.auth.GoogleAuthProvider.PROVIDER_ID,
      firebase.auth.EmailAuthProvider.PROVIDER_ID
    ]
  };

  firebase.auth().onAuthStateChanged(function(user) {
    if (user) {
      document.getElementById('sign-out').hidden = false;
      //  document.getElementById('login-info').hidden = false;
      console.log('Signed in as ${user.displayName} (${user.email})');
      user.getIdToken().then(function(token) {
        document.cookie = "token=" + token;
      });
    } else {
      var ui = new firebaseui.auth.AuthUI(firebase.auth());
      ui.start('#firebase-auth-container', uiConfig);
      document.getElementById('sign-out').hidden = true;
      //  document.getElementById('login-info').hidden = true;
      document.cookie = "token=";
    }
  }, function(error) {
    console.log(error);
    alert('Unable to log in: ' + error);
  });




});