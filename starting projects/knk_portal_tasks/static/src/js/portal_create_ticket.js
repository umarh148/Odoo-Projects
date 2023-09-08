odoo.define('knk_portal_tasks.create', function (require) {
'use strict';

var publicWidget = require('web.public.widget');

publicWidget.registry.ScheduleMeetingLayout = publicWidget.Widget.extend({
    selector: '#website_meeting_form',
    events: {
        'change select.set-issue-type': '_onApplyTimeslotsChange',
        'change input.set-issue-type': '_onApplyTimeslotsChange',
        'submit':function(i,j){
            debugger;
        }
    },

    init: function (parent, params) {
        this._super.apply(this, arguments);
        $("#timezone").val(Intl.DateTimeFormat().resolvedOptions().timeZone);
        this._onApplyTimeslotsChange();
        Dropzone.autoDiscover = false;
        
        //let dropzone = new Dropzone("div#attachment-tickets", dropzoneParams);
        

    },

    /**
     * @private
     * @param {Event} ev
     */
    _onApplyTimeslotsChange: function (ev) {
        // let duration = 0;
        // const employeeUserId = Number($("#employee").selected()[0].value);
        // if ($("#fifteen_minutes")[0].checked) duration = 15;
        // else if ($("#thirty_minutes")[0].checked) duration = 30;
        // else if ($("#forty_five_minutes")[0].checked) duration = 45;
        // else if ($("#sixty_minutes")[0].checked) duration = 60;
        // let meetingDate = $("#meeting_date")[0].value;
        // const meetingDateObj = new Date(meetingDate);
        // const timezone = $("#timezone").selected()[0].value;
        // if (meetingDateObj.toDateString() === 'Invalid Date') {
        //     meetingDate = new Date().toLocaleDateString('en-CA');
        //     $("#meeting_date")[0].value = meetingDate;
        // }
        // return this._rpc({
        //         model: 'calendar.event',
        //         method: 'get_available_time_slots',
        //         args: [employeeUserId, duration, meetingDate, timezone],
        //     })
        //     .then(function (options) {
        //         var $el = $("#timeslot");
        //         $el.empty(); // remove old options
        //         $.each(options, function(key,value) {
        //           $el.append($("<option></option>")
        //              .attr("value", value).text(key));
        //         });
        //     });
    },
});
});
