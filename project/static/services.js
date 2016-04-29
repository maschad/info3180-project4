/**
 * Created by chad on 4/2/16.
 */

angular.module('myApp')

.factory('AuthService', ['$q', '$timeout', '$http', function ($q, $timeout, $http) {
    var user = null;
    return ({
      isLoggedIn: isLoggedIn,
      login: login,
      logout: logout,
        register: register
    });

    function isLoggedIn() {
        return !!user;
    }

    function login(email,password) {
        var deferred = $q.defer();

        $http.post('/api/user/login', {email: email, password: password})
            .success(function (data, status) {
                if (status == 200 && data) {
                user = true;
                deferred.resolve();
            }else{
                user = false;
                deferred.reject();
            }
        })
        .error(function (data) {
            user = false;
            deferred.reject();
        });

        return deferred.promise;
    }
    
    function logout() {
        var deferred = $q.defer();

        $http.get('/api/user/logout')
            .success(function (data) {
                user = false;
                deferred.resolve();
            })
            .error(function (data) {
                user = false;
                deferred.reject();
            });
        return deferred.promise;
    }
    
    function register(email, password,name) {
        var deferred = $q.defer();

        $http.post('/api/user/register', {email: email, password: password, name: name})
            .success(function (data, status) {
                if(status==200 && data.result == 'success'){
                    deferred.resolve();

                }else if (data.result == 'user already registered'){
                    deferred.reject();
                }
            })
            .error(function (data) {
                deferred.reject();
            });

        return deferred.promise;
    }

}])
    
.factory('ItemManagerService',['$q','$http', function ($q, $http) {
    return({
        storeItem : storeItem,
        removeItem : removeItem
    });

    //Store Item in database
    function storeItem(item, user) {
        var deferred = $q.defer();

        $http.post('/api/user/' + user.id + '/wishlist')
            .success(function (data, status) {
                if(status==200 &&data.result){
                    deferred.resolve();
                }else{
                    deferred.reject();
                }
            })
            .error(function (data) {
                deferred.reject();
            });
        return deferred;
    }

    //Remove an item from the database
    function removeItem() {

    }
}]);

