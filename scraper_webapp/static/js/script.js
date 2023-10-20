$(function() {
    $("#budget-slider").slider({
        range: true,
        min: 0,
        max: 20000,
        values: [8000, 10000],  
        create: function() {
            positionHandleValues();
        },
        slide: function(event, ui) {
            $("input[name='lower_budget']").val(ui.values[0]);
            $("input[name='upper_budget']").val(ui.values[1]);
            positionHandleValues(ui.values);
        }
    });

    $("#budget-range").text("Kr" + $("#budget-slider").slider("values", 0) + " - Kr" + $("#budget-slider").slider("values", 1));

    function positionHandleValues(values) {
        values = values || $("#budget-slider").slider("values");
        var handleValues = [$("#lower-handle-value"), $("#upper-handle-value")];
        var handles = $("#budget-slider .ui-slider-handle");
        handleValues[0].text(values[0]+',-');
        handleValues[1].text(values[1]+',-');
        handleValues.forEach(function(handleValue, index) {
            handleValue.css({
                "left": handles.eq(index).position().left - (handleValue.outerWidth() - handles.eq(index).outerWidth()) / 2 + "px",
                "top": handles.eq(index).position().top - handleValue.outerHeight() - 4 + "px"  // Adjust this value to change the vertical spacing
            });
        });
    }

    function createSliderScale(min, max, step) {
        var scaleContainer = $('#slider-scale');
        scaleContainer.empty(); 
        for (var i = min; i <= max; i += step) {
            var scaleLabel = $('<span>').text(i + ' kr').css({
                'flex': '1',
                'text-align': (i === min ? 'left' : (i === max ? 'right' : 'center'))
            });
            scaleContainer.append(scaleLabel);
        }
    }

    function resetForm() {
        
        $('#pcBuilderForm')[0].reset();
        $("#budget-slider").slider("values", [8000, 10000]); // Reset slider to initial values
        positionHandleValues($("#budget-slider").slider("values"));
    }

    $("#priority-slider").slider({
        range: "min",
        min: 0,
        max: 100,
        value: 50,  // Setting the initial value to 50 (midway) as an example.
        slide: function(event, ui) {
            // Any logic you want to add while sliding.
        }
    });

    $(document).ready(function() {
        $("#cooling-slider").slider({
            range: "min",
            min: 1,
            max: 10,  // Adjust the max value based on your requirements.
            value: 5, // Default value at initialization
            slide: function(event, ui) {
                // Update the hidden input value when the slider value changes
                $("#coolingValue").val(ui.value);
            }
        });
    
        // Initialize the hidden input value with the slider's initial value
        $("#coolingValue").val($("#cooling-slider").slider("value"));
    });

    $(document).ready(function() {
        $("#aesthetics-slider").slider({
            range: "min",
            min: 1,
            max: 10,  // Adjust the max value based on your requirements.
            value: 5, // Default value at initialization
            slide: function(event, ui) {
                // Update the hidden input value when the slider value changes
                $("#aestheticsValue").val(ui.value);
            }
        });
    
        // Initialize the hidden input value with the slider's initial value
        $("#aestheticsValue").val($("#aesthetics-slider").slider("value"));
    });

    createSliderScale(0, 20000, 5000);
    window.resetForm = resetForm;
});
