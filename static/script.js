const COLORS = ['#FE9', '#9AF', '#F9A', "#AFA", "#FA7"];

// var items = '{ "yandex.ru": "Вася", "age": 35, "isAdmin": false, "friends": [0,1,2,3] }';
const items = ['yandex.ru', 'google.ru', 'wtf.ru'];

function addItem(container, template, id) {
  let color = COLORS[_.random(COLORS.length - 1)];
  let num = _.random(10000);

  container.append(Mustache.render(template, {
    color,
    num
  }));
}

$(() => {
  $.get( "ajax/test.html", function( data ) {
    $( ".result" ).html( data );
    alert( "Load was performed." );
  });
}
)

// $(() => {
//   const tmpl = $('#item_template').html()
//   const container = $('#app');


//   // for (var i in items) {
//   //     addItem(container, tmpl, items[i])
//   // }
//   for (let i = 0; i < 10; i++) {
//     addItem(container, tmpl, 1);
//   }

//   // $('#add_el').click(() => {
//   //   addItem(container, tmpl);
//   // })

//   container.on('click', '.del_el', (e) => {
//     $(e.target).closest('.item').remove();
//   });
// });
