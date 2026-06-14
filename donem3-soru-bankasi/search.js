function microSearch(query){
  var q = query.trim().toLocaleLowerCase('tr');
  var visible = 0, total = 0;

  document.querySelectorAll('.topic-card').forEach(function(card){
    total++;
    var haps = card.querySelectorAll('.hap-item');
    var show;
    if(q === ''){
      haps.forEach(function(h){ h.style.display = ''; });
      show = true;
    } else if(haps.length){
      var header = card.querySelector('.topic-header');
      var titleMatch = header && header.textContent.toLocaleLowerCase('tr').includes(q);
      var anyMatch = false;
      haps.forEach(function(h){
        var match = titleMatch || h.textContent.toLocaleLowerCase('tr').includes(q);
        h.style.display = match ? '' : 'none';
        if(match) anyMatch = true;
      });
      show = anyMatch;
    } else {
      show = card.textContent.toLocaleLowerCase('tr').includes(q);
    }
    card.style.display = show ? '' : 'none';
    if(show) visible++;
  });

  document.querySelectorAll('.nav-card').forEach(function(nc){
    total++;
    var show = q === '' || nc.textContent.toLocaleLowerCase('tr').includes(q);
    nc.style.display = show ? '' : 'none';
    if(show) visible++;
  });

  var msg = document.getElementById('searchNoResult');
  if(q !== '' && total > 0 && visible === 0){
    if(!msg){
      msg = document.createElement('div');
      msg.id = 'searchNoResult';
      msg.className = 'note';
      var main = document.querySelector('main');
      main.insertBefore(msg, main.firstChild);
    }
    msg.textContent = '🔍 "' + query.trim() + '" için sonuç bulunamadı.';
  } else if(msg){
    msg.remove();
  }
}
