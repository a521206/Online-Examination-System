// question_type_toggle.js
(function($) {
    function toggleFields() {
        var qtype = $('#id_question_type').val();
        if (qtype === 'MCQ') {
            $('[id^="id_optionA"], [id^="id_optionB"], [id^="id_optionC"], [id^="id_optionD"], [id^="id_mcq_answer"]').closest('.form-row, .form-group, .field-optionA, .field-optionB, .field-optionC, .field-optionD, .field-mcq_answer').show();
            $('[id^="id_short_answer"]').closest('.form-row, .form-group, .field-short_answer').hide();
        } else if (qtype === 'SHORT') {
            $('[id^="id_optionA"], [id^="id_optionB"], [id^="id_optionC"], [id^="id_optionD"], [id^="id_mcq_answer"]').closest('.form-row, .form-group, .field-optionA, .field-optionB, .field-optionC, .field-optionD, .field-mcq_answer').hide();
            $('[id^="id_short_answer"]').closest('.form-row, .form-group, .field-short_answer').show();
        } else {
            // Show all by default
            $('[id^="id_optionA"], [id^="id_optionB"], [id^="id_optionC"], [id^="id_optionD"], [id^="id_mcq_answer"], [id^="id_short_answer"]').closest('.form-row, .form-group, .field-optionA, .field-optionB, .field-optionC, .field-optionD, .field-mcq_answer, .field-short_answer').show();
        }
    }
    $(document).ready(function() {
        toggleFields();
        $('#id_question_type').change(toggleFields);
    });
})(django.jQuery); 