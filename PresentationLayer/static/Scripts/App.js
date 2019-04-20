var App = (function () {

    return {
        OpenLinkInDiv: function (link, divSelector) {
            $(divSelector).empty();
            App.ShowLoading(divSelector);
            $(divSelector).load(link, function () { App.HideLoading(divSelector) });
        },
        PostJsonAndOpenInDiv: function(url , elemSelector , divSelector){
            $(divSelector).empty();
            App.ShowLoading(divSelector);

            $.ajax({
                url: url,
                dataType: 'text',
                type: 'post',
                contentType: 'application/json',
                data: $(elemSelector).val(),
                success: function( data, textStatus, jQxhr ){
                    $(divSelector).html( data );
                }
            });
        },
        ShowLoading: function (divSelector) {
            $(divSelector).append($( '<i class="loading-circle fa fa-circle-o-notch fa-spin" ></i>'));
        },

        HideLoading: function (divSelector) {
            $(divSelector).remove("i");
        }
    }
})()
