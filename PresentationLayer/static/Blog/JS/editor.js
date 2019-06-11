var toolbarOptions = [
  ['bold', 'italic', 'underline', 'strike'],        // toggled buttons
  ['blockquote', 'code-block'],

  [{ 'header': 1 }, { 'header': 2 }],               // custom button values
  [{ 'list': 'ordered'}, { 'list': 'bullet' }],
  [{ 'script': 'sub'}, { 'script': 'super' }],      // superscript/subscript
  [{ 'indent': '-1'}, { 'indent': '+1' }],          // outdent/indent
  [{ 'direction': 'rtl' }],                         // text direction

  [{ 'size': ['small', false, 'large', 'huge'] }],  // custom dropdown
  [{ 'header': [1, 2, 3, 4, 5, 6, false] }],

  [{ 'color': [] }, { 'background': [] }],          // dropdown with defaults from theme
  [{ 'font': [] }],
  [{ 'align': [] }],
  ['image'],

  ['clean']                                         // remove formatting button
];


var BlogEditor = (function(jq){

  var _endpoint;
  var _editors = {};
  var Editor = function(selector){
     _editors[selector] = new Quill(selector, {
      modules: {
        toolbar: toolbarOptions,
        imageResize: {
              modules: [ 'Resize', 'DisplaySize', 'Toolbar' ]
          }
      },
      theme: 'snow'
    })

    return _editors[selector]
  };

  var GetEditor = function(selector){
    return _editors[selector]
  }

  var Save = function(selector , id){
    var editor = GetEditor(selector)
    $.ajax( {
        url:_endpoint,
        method: "POST",
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        data: JSON.stringify({"id":id , "content":editor.getContents()})
    });
  }

  return {

    CreateEditor: Editor,
    Save: Save,
    SetEndPoint: function(ep){
      _endpoint = ep
    }
  }

})($);
