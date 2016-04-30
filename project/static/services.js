/**
 * Created by chad on 4/2/16.
 */

angular.module('myApp').factory('AuthService', ['$q', '$timeout', '$http', '$cookies', function ($q, $timeout, $http, $cookies) {
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
                    $cookies.put('online', true);
                    $cookies.put('id', data.id);
                    $cookies.put('token', data.token);
                    $cookies.put('name', data.name);
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
                $cookies.put('online', false);
                $cookies.remove('token');
                $cookies.remove('id');
                $cookies.remove('name');
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

    .factory('ItemManagerService', ['$q', '$http', '$cookies', function ($q, $http, $cookies) {
    return({
        storeItem: storeItem,
        removeItem: removeItem
    });

    //Store Item in database
        function storeItem(item) {
        var deferred = $q.defer();
            $http.post('/api/user/' + $cookies.get('id') + '/wishlist', item)
            .success(function (data, status) {
                if (status == 200 && data) {
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
        function removeItem(itemId) {
            var deferred = $q.defer();

            $http.post('/api/user/' + $cookies.get('id') + itemId + '/wishlist')
                .success(function (data, status) {
                    if (status == 200 && data) {
                        deferred.resolve();
                    } else {
                        deferred.reject();
                    }
                })
                .error(function (data) {
                    deferred.reject();
                });
            return deferred;
    }
}]);

