(function () {
    'use strict';
  
      angular.module('WordcountApp', ['nvd3ChartDirectives'])
  
      .controller('WordcountController', ['$scope', '$log', '$http','$timeout',
        function($scope, $log, $http, $timeout) {
        $scope.submitButtonText = 'Submit';
        $scope.loading = false;
        $scope.nullLocations = 0;
        $scope.getResults = function() {
          
          // get the URL from the input
          var userInput = $scope.keyword;
          var userPosition = $scope.position;
  
          // fire the API request
          $http({
              url: '/start',
              method: "GET",
              params: {"keyword": userInput,
                       "position": userPosition,
                       "result": "trends"}
          }).
            success(function(results) {
              $log.log(results);
              getTrends(results, userInput);
              $scope.loading = true;
              $scope.submitButtonText = 'Loading...';
            }).
            error(function(error) {
              $log.log(error);
            });
  
        };
  
      function getTrends(jobID, userInput) {
  
        var timeout = '';
  
        var poller = function() {
          // fire another request
          $http.get('/get_results?result=trends&job_key='+jobID).
            success(function(data, status, headers, config) {
              if(status === 202) {
                $log.log(data, status);
                } else if (status === 200){
                  $log.log(data);
                  createChart(data[0], $scope, userInput, $log);
                  $scope.loading = false;
                  $scope.submitButtonText = "Submit";
                  //$scope.wordcounts = data;
                  $timeout.cancel(timeout);
                  return false;
                }
                // continue to call the poller() function every 2 seconds
                // until the timeout is cancelled
                timeout = $timeout(poller, 2000);
            }).
            error(function(error) {
              $log.log(error);
              $scope.loading = false;
              $scope.submitButtonText = "Submit";
              //$scope.urlerror = true;
            });
        };
  
        poller();
  
      }
      
      function createChart(data, $scope, userInput) {
          $("#chartTitle").show();
          var values = [];
          var i = 0;
          for (var word in data) {
              values.push([ Number(word), data[word]]);
          }
          $scope.wordcounts = values;
          $scope.keywordData = [{
              "key": userInput,
              "bar": true,
              "values": values
          }];
      }}]);
  
  }());