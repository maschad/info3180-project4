var myApp = angular.module('myApp', ['ngRoute', 'ngCookies']);

myApp.config(function ($routeProvider) {
  $routeProvider
      .when('/home', {
      templateUrl: 'static/partials/home.html',
      controller: 'homeController'
    })
    .when('/login',{
      templateUrl: 'static/partials/login.html',
      controller: 'loginController'

    })
      .when('/add', {
        templateUrl: 'static/partials/add.html',
        controller: 'addController'
    })
    .when('/register', {
      templateUrl: 'static/partials/register.html',
      controller: 'registerController'

    })
    .when('/one', {
      template: '<h1>This is page one!</h1>',

    })
    .when('/two', {
      template: '<h1>This is page two!</h1>',

    })
    .otherwise({
      redirectTo: '/login'
    });
});

myApp.run(['$cookies', '$rootScope', function ($cookies, $rootScope) {
  if (!$cookies.get('online')) {
    $cookies.put('online', false);
    $rootScope.user = false;
  } else if ($cookies.get('online') === 'true') {
    $rootScope.user = true;
  }
}]);