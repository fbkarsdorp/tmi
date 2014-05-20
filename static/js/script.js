var app = angular.module('app',['ngRoute']);

app.config(function($routeProvider, $locationProvider) {
	$routeProvider
	.when('/', {templateUrl: "static/templates/search.html",controller:'search'})
	.otherwise( { redirectTo: '/'});
	
	$locationProvider.html5Mode(true);

})

app.run(function($interval,$rootScope,$location,$http){


})

/* Controllers ------------------------------------------------ */

app.controller("search",function($scope,$http,$timeout){

    $scope.page = 1;
    $scope.pagecount = 99;
    $scope.no_results=false;

    $scope.search = function(q,page){
        $scope.q = q;
        $scope.page = page ? page : 1;
        if(page<1){page = 1;}
        if($scope.data){
            if(page>$scope.data.pagecount){page = $scope.data.pagecount;}
        }
        if(q==""){
            $scope.data = "";
            $scope.$apply();
        } else {
            $scope.loading = true;
            $scope.data = "loading";
            $http.post("api",{q:$scope.q,page:$scope.page}).success(function(data){
                $scope.data = data;
                $scope.pagecount = data.pagecount;
                $scope.loading = false;
            }).error(function(){
                $scope.loading = false;
            })
        }
    }
    $scope.download = function(){
        window.open("/download?q="+$scope.q);
    } 
    $scope.search_button = function(){
        $scope.search($scope.q);
    }
    $scope.sugsearch = function(q){
        if(q.match(" ")){q = "wn:\""+q+"\""} else {q = "wn:"+q;};
        $scope.search(q);
    } 
    $scope.check_results = function(){
        if($scope.data){
            if($scope.data.hits<1 && !$scope.loading){return true;}
        }
        return false;
    }
    $scope.pages = function(){
        var pages = [];
        var p = $scope.page-4;
        if(p<1){p = 1;}
        var pagecount = $scope.pagecount ? $scope.pagecount : 999;
        for(var i = p; i < (p+10) && i <= pagecount; i++){
            pages.push(i);
        }
        return pages;
    } 
    $("*[zoek]").focus();
    $(window).on("keydown",function(e){
        if(e.keyCode==27){
            if($scope.q=="wn:fantasm"){
                $scope.search("");
            } else {
                $scope.search("wn:fantasm");
            }
        }
    })
    $scope.is_first = function(){
        if($scope.page == 1) return false
        return true;
    }
    $scope.is_last = function(){
        if($scope.data){
            if($scope.page == $scope.data.pagecount){
                return false
            }
        }
        return true;
    }
})

/* Directives ------------------------------------------------- */

app.directive("zoek",function($http){
	return {
		restrict:"A",
		link:function(scope,element,attrs){
			element.on("keydown",function(e){
				if(e.keyCode=="13"){
					scope.search(element.val());
				}
			})
		}
	}
})

app.directive("fixed",function($http,$rootScope){
    return {
        restrict:"A",
        link:function(scope,element,attrs){
            var pos = 0;
            $("#frame").scroll(function () {
                var pos = $("#frame").scrollTop();
                if(pos>attrs['fixed']){
                    element.addClass("fixed");
                } else {
                    element.removeClass("fixed");
                }
            });
        }
    }
})

app.directive("prefix",function($http,$rootScope){
    return {
        restrict:"A",
        link:function(scope,element,attrs){
            var pos = 0;
            $("#frame").scroll(function () {
                var pos = $("#frame").scrollTop();
                if(pos>attrs['prefix']){
                    element.addClass("prefix");
                } else {
                    element.removeClass("prefix");
                }
            });
        }
    }
})

app.directive("help",function($http){
    return {
        restrict:"A",
        templateUrl: "static/templates/help.html"
    }
})

/* Filters ---------------------------------------------------- */

app.filter('htmll', ['$sce', function($sce){
    return function(text) {
        return $sce.trustAsHtml(text);
    };
}]);

app.filter("round",function(){
    return function(ms){
        return (Math.round(ms * 1000) / 1000)+"ms";
    }
})