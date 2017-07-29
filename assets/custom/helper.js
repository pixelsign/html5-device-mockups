var getScroll = function() {
	if (window.pageYOffset != undefined) {
		return [pageXOffset, pageYOffset];
	} else {
		var sx, sy, d = document,
			r = d.documentElement,
			b = d.body;
		sx = r.scrollLeft || b.scrollLeft || 0;
		sy = r.scrollTop || b.scrollTop || 0;
		return [sx, sy];
	}
}
window.onscroll = function(e) {
	var iHScroll = getScroll()[1];
	if (iHScroll > 20) {
		//
	} else {
		//
	}
}

$(function() {
	$.fn.goTo = function() {
		$('body').animate({
			scrollTop: $(this).position().top + 'px'
		}, 'slow');
		return this;
	}
});
