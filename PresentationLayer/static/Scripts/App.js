var App = (function () {

    return {
        OpenLinkInDiv: function (link, divSelector) {
            $(divSelector).empty();
            this.ShowLoading(divSelector);
            $(divSelector).load(link, function () { this.HideLoading(divSelector) });
        },

        ShowLoading: function (divSelector) {
            $(divSelector).append($( '<i class="loading-circle fa fa-circle-o-notch fa-spin" ></i>'));
        },

        HideLoading: function (divSelector) {
            $(divSelector).remove("i");
        }
    }
})()