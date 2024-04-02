(function($) {
    "use strict";

    function initDragula() {
        $('[data-plugin="dragula"]').each(function() {
            var containers = $(this).data("containers"),
                dragulaContainers = [];

            if (containers) {
                for (var i = 0; i < containers.length; i++) {
                    dragulaContainers.push($('#' + containers[i])[0]);
                }
            } else {
                dragulaContainers = [$(this)[0]];
            }

            var handleClass = $(this).data("handleclass");
            var drake = handleClass ? dragula(dragulaContainers, {
                moves: function(el, container, handle) {
                    return handle.classList.contains(handleClass);
                }
            }) : dragula(dragulaContainers);

            drake.on('drop', function(el, target, source, sibling) {
                var columnData = {};

                dragulaContainers.forEach(function(container) {
                    var taskIds = Array.from(container.children).map(function(task) {
                        return task.getAttribute('task_id');
                    });

                    var columnId = $(container).attr('id');
                    columnData[columnId] = taskIds;
                });

                console.clear();
                console.log(columnData);

                // Envia os IDs via AJAX GET quando necessário
                sendColumnData(columnData);
            });
        });
    }

    function sendColumnData(columnData) {
        // Constrói o JSON com os IDs das colunas
        var jsonData = JSON.stringify(columnData);

        // Substitua "YOUR_URL_HERE" pelo seu URL de destino
        var url = "YOUR_URL_HERE?data=" + encodeURIComponent(jsonData);

        // Envia o JSON via AJAX GET
        $.ajax({
            url: url,
            type: "GET",
            success: function(response) {
                console.log("Data sent successfully:", response);
            },
            error: function(xhr, status, error) {
                console.error("Error:", error);
            }
        });
    }

    window.Dragula = {
        init: initDragula
    };

    $(document).ready(function() {
        Dragula.init();
    });
})(window.jQuery);
