var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
var CognitoUser = AmazonCognitoIdentity.CognitoUser;
var AuthenticationDetails = AmazonCognitoIdentity.AuthenticationDetails;

var poolData = {
    UserPoolId : 'us-east-2_4NELA3imh',
    ClientId : '3kl9bhn4bst09fbpo3mc2s3mo6'
};


function login () {
    var username = $('#username').val();
    var password = $('#password').val();

    var authenticationData = {
        Username : username,
        Password : password,
    };

    var authenticationDetails = new AuthenticationDetails(authenticationData);
    var userPool = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserPool(poolData);

    var userData = {
        Username : username,
        Pool : userPool
    };

    var cognitoUser = new CognitoUser(userData);

    cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: function (result) {
            console.log("SUCCESS");
            // console.log(result.getAccessToken().getJwtToken());
            window.location.href = "/home";
        },

        onFailure: function(err) {
            console.log("FAIL");
            alert(err);
        }

    });
}

function signOut () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    if (cognitoUser !== null) {
        cognitoUser.signOut();
    }
    window.location.href = "/";
}

function search() {
    var keyword = $('#keyword').val();
    s = "/home/keyword/" + keyword;
    console.log(s);
    window.location.href = s;
}

function signup () {
    var username = $('#username').val();
    var password = $('#password').val();
    var email = $('#email').val();

    var userPool = new CognitoUserPool(poolData);
    var userAttributes = [];

    var dataEmail = {
        Name : 'email',
        Value : email
    };

    var attributeEmail = new AWSCognito.CognitoIdentityServiceProvider.CognitoUserAttribute(dataEmail);

    userAttributes.push(attributeEmail);

    userPool.signUp(username, password, userAttributes, null, function(err, result){
        if (err) {
            alert(err);
            return;
        }
        cognitoUser = result.user;
        console.log('user name is ' + cognitoUser.getUsername());
        window.location.href = "/confirmUser";
    });
}


function validate () {
    var username = $('#usernameInput').val();
    var code = $('#codeInput').val();

    var userPool = new CognitoUserPool(poolData);

    var userData = {
        Username : username,
        Pool : userPool
    };

    var cognitoUser = new CognitoUser(userData);
    cognitoUser.confirmRegistration(code, true, function(err, result) {
        if (err) {
            alert(err);
            return;
        }
        console.log('call result: ' + result);
        window.location.href = "/login";
    });
}

function setWelcome () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            if (session.isValid()) {
                // console.log("Session validity: " + session.isValid());
                // console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
                // // $('#myName').html(cognitoUser.username);
                // console.log("Returning");
                // return "A";
                // console.log("Returning")
                // return "A";
            }
            else {
                console.log("here2");
                signOut();
            }
            
        });
    }
    else {
        console.log("Her222222222e");
        signOut();
        return;
    }
    console.log("Here also");
    return cognitoUser.username;

    // var url = "/api/protected_api";

    // $.post(url, {'access_token':
    //     cognitoUser.signInUserSession.accessToken.jwtToken})
    // .done(function (data) {
    //     $('#data_from_protected_api').html(data);
    // });
}   

function upload () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();

    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            if (session.isValid()) {
                console.log("session validity" + session.isValid());
                console.log(cognitoUser.signInUserSession.accessToken.jwtToken);
                $('#username').html(cognitoUser.username);

                var image_path = $('#image_path').val();
                var image_caption = $('#image_caption').val();
                console.log(image_path);
                console.log(image_caption);
                console.log(cognitoUser.username)
                var file = document.querySelector('input[type=file]').files[0];
                console.log(file)

                var formData = new FormData();
                formData.append('image', file);
                formData.append('username', cognitoUser.username);
                formData.append('image_caption', image_caption)
                $.ajax({
                    type: 'POST',
                    url: '/upload',
                    data: formData,
                    processData: false,  // prevent jQuery from converting the data
                    contentType: false,  // prevent jQuery from overriding content type
                    success: function(response) {
                        alert(response);
                    }
                });

            }
            else {
                console.log("here2");
                signOut();
            }
            
        });
    }
    else {
        signOut();
    }
}