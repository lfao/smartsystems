
/* globals NGSI $ */
/* exported Example */

var Example = (function () {

    "use strict";

    // =========================================================================
    // CLASS DEFINITION
    // =========================================================================

    var buildNGSIConnection = function buildNGSIConnection() {
        // Creating a connection to the Context Broker
        this.ngsi_server = MashupPlatform.prefs.get('ngsi_server');
        this.ngsi_proxy = MashupPlatform.prefs.get('ngsi_proxy');

        var request_headers = {};

        var tenant = MashupPlatform.prefs.get('ngsi_tenant').trim().toLowerCase();
        if (tenant !== '') {
            request_headers['FIWARE-Service'] = tenant;
        }

        var path = MashupPlatform.prefs.get('ngsi_service_path').trim().toLowerCase();
        if (path !== '' && path !== '/') {
            request_headers['FIWARE-ServicePath'] = path;
        }

        this.connection = new NGSI.Connection(this.ngsi_server, {
            request_headers: request_headers,
            ngsi_proxy_url: this.ngsi_proxy
        });
    };

    var commandHandler = function commandHandler() {
        // Send command using a NGSI  updateContext
        this.connection.updateAttributes([{
            'entity': {id: 'id'},
            'attributes': [
                {name: 'turn', contextValue: 'value'}
            ]
        }], {
            onSuccess: commandWaitHandler.bind(this, 0)
        });
    };

    var Example = function Example() {
        this.connection = null;

        buildNGSIConnection.call(this);

        MashupPlatform.prefs.registerCallback(function () {
            buildNGSIConnection.call(this);
        }.bind(this));

        MashupPlatform.wiring.registerCallback('clouds', function (data) {
            // Callback for wiring events
            var tmp = JSON.parse(data);
            alert(tmp.Clouds);
            var clouds = tmp.Clouds;
            
            function showImage() {
                switch(true) {
                        case(clouds <= 20):
                            alert(clouds);
                            break;
                        case(clouds <= 40 && clouds > 20):
                            break;
                        case(clouds <= 60 && clouds > 40):
                            break;
                        case(clouds <= 80 && clouds > 60):
                            break;
                        case(clouds <= 100 && clouds > 80):
                            break;
                                  }
                var img = document.getElementById('myImageId');
                img.style.visibility = 'visible';
            }
            // Query the context broker
            this.connection.query([{
                id: 'id'
            }], null, {
                flat: true,
                onSuccess: () => {}
            });
        }.bind(this));
    };

    return Example;

})();
