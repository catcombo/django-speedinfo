// Based on https://makandracards.com/makandra/24451-sticky-table-header-with-jquery
(function ($) {
    $.fn.fixedHeader = function () {
        return this.each(function () {
            var table = $(this), tableFixed;

            function init() {
                tableFixed = table.clone();
                tableFixed.find('tbody').remove().end().addClass('fixed-header').insertBefore(table);
                resizeFixed();
            }

            function resizeFixed() {
                tableFixed.find('th').each(function (index) {
                    $(this).css('min-width', table.find('th').eq(index).width()+'px');
                });
            }

            function scrollFixed() {
                var offset = $(this).scrollTop(),
                    tableOffsetTop = table.offset().top,
                    tableOffsetBottom = tableOffsetTop + table.height() - table.find('thead').height();

                if (offset < tableOffsetTop || offset > tableOffsetBottom)
                    tableFixed.hide();
                else if (offset >= tableOffsetTop && offset <= tableOffsetBottom && tableFixed.is(':hidden'))
                    tableFixed.show();

                tableFixed.css('left', table.offset().left - $(this).scrollLeft());
            }

            $(window).on('resize', resizeFixed);
            $(window).on('scroll', scrollFixed);

            init();
        });
    };
})(django.jQuery);
