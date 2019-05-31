var CognitoUserPool = AmazonCognitoIdentity.CognitoUserPool;
var CognitoUser = AmazonCognitoIdentity.CognitoUser;
var AuthenticationDetails = AmazonCognitoIdentity.AuthenticationDetails;

var poolData = {
    UserPoolId : '<PUT_APPROPRIATE_VALUE_HERE>',
    ClientId : '<PUT_APPROPRIATE_VALUE_HERE>'
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
    window.location.href = "/login";
}

function search() {
    var keyword = $('#keyword').val();
    keyword = keyword.trim().replace("#","");
    console.log("Searching by keyword ", keyword.trim())
    if (keyword == "") {
        console.log("Blank search")
    }
    else {
        s = "/home/keyword/" + keyword;
        console.log(s);
        window.location.href = s;
    }
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
        console.log('User name is ' + cognitoUser.getUsername());
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
        window.location.href = "/login";
    });
}

function checkSession () {
    var userPool = new CognitoUserPool(poolData);
    var cognitoUser = userPool.getCurrentUser();
    if (cognitoUser != null) {
        cognitoUser.getSession(function(err, session) {
            if (err) {
                alert(err);
                return;
            }
            if (!session.isValid()) {
                console.log("User not authorized");
                signOut();
            }
            
        });
    }
    else {
        signOut();
        return;
    }
    return cognitoUser.username;
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
                $('#username').html(cognitoUser.username);

                var image_path = $('#image_path').val();
                var image_caption = $('#image_caption').val();
                var file = document.querySelector('input[type=file]').files[0];

                var formData = new FormData();
                formData.append('image', file);
                formData.append('username', cognitoUser.username);
                formData.append('image_caption', image_caption)
                $.ajax({
                    type: 'POST',
                    url: '/upload',
                    data: formData,
                    processData: false, 
                    contentType: false, 
                    success: function(response) {
                        alert(response);
                    }
                });

            }
            else {
                console.log("Not authorized");
                signOut();
            }
            
        });
    }
    else {
        signOut();
    }
}