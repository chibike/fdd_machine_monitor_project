function open_tab(url, parameters)
{
  var query_url = window.location.origin + "/" + url + "?t=" + (new Date).getTime();
  if (parameters)
  {
    query_url += "&" + parameters;
  }

  window.open(query_url, "_newtab");
}

function getJSON(ref, url, callback, parameters)
{
    var xhr = new XMLHttpRequest();
    var query_url = window.location.origin + "/" + url + "?t=" + (new Date).getTime();

    if (parameters)
    {
      query_url += "&" + parameters;
    }

    xhr.open('GET', query_url, true);
    xhr.responseType = 'json';
    xhr.onload = function()
    {
      var status = xhr.status;
      if (status === 200) { callback(ref, null, xhr.response); }
      else { callback(ref, status, xhr.response); }
    };
    xhr.send();
}