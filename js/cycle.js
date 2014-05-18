var Dom = {
	get: function(el) {
		if (typeof el === 'string') {
			return document.getElementById(el);
		} else {
			return el;
		}
	},
	add: function(el, dest) {
		var el = this.get(el);
		var dest = this.get(dest);
		dest.appendChild(el);
	},
	remove: function(el) {
		var el = this.get(el);
		el.parentNode.removeChild(el);
	}
};

var Event = {
	add: function() {
		if (window.addEventListener) {
			return function(el, type, fn) {
				Dom.get(el).addEventListener(type, fn, false);
			};
		} else if (window.attachEvent) {
			return function(el, type, fn) {
				var f = function() {
					fn.call(Dom.get(el), window.event);
				};
				Dom.get(el).attachEvent('on' + type, f);
			};
		}
	}()
};

/* http://www.dustindiaz.com/getelementsbyclass/ */
function getElementsByClass(searchClass, node, tag) {
	var classElements = new Array();
	if (node == null)
		node = document;
	if (tag == null)
		tag = '*';
	var els = node.getElementsByTagName(tag);
	var elsLen = els.length;
	var pattern = new RegExp("(^|\\s)"+searchClass+"(\\s|$)");
	for (var i=0,j=0;i<elsLen;i++) {
		if (pattern.test(els[i].className)) {
			classElements[j] = els[i];
			j++;
		}
	}
	return classElements;
}

function cycle(tag) {
	return (' ' + tag.className + ' ').indexOf(' cycle ') > -1;
}

function showNext(curr) {
	return function() {
		var tag = curr.tagName;
		var next = curr.nextElementSibling;
		if (next == null || !cycle(next)) {
			next = curr;
			var prev = next.previousElementSibling;
			while (prev != null && cycle(prev)) {
				next = prev;
				prev = next.previousElementSibling;
			}
		}
		if (next != curr) {
			next.className += " show";
			curr.className = curr.className.replace(" show", "");
			// change imgsrc
			if (tag.toLowerCase() == 'img') {
				var article = next.parentNode;
				var imgSrcs = 
					getElementsByClass('imgsrc', article, null);
				if (imgSrcs != null)
					imgSrcs[0].innerText = next.alt;
			}
		}
	};
}
function stopClick(evt) {
	evt.preventDefault();
	return false;
}

function initCycle() {
	var items = getElementsByClass('cycle', null, null);
	for (var i=0;i<items.length;i++) {
		var item = items[i];
		Event.add(item, 'click', showNext(item));
		Event.add(item, 'click', stopClick);
	}
}
