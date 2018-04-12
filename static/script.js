//const COLORS = ['#FE9', '#9AF', '#F9A', "#AFA", "#FA7"];
const COLORS = ["#0F0"];
const OK_COLOR = "#0F0";

// var items = '{ "yandex.ru": "Вася", "age": 35, "isAdmin": false, "friends": [0,1,2,3] }';
const items = ['yandex.ru', 'google.ru', 'wtf.ru'];

function addItem(container, template, id) {
  //let color = COLORS[_.random(COLORS.length - 1)];
  let color = OK_COLOR;
  let num = _.random(10000);

  container.append(Mustache.render(template, {
    color,
    id
  }));
}

$(() => {
    const container = $('#app');
    const tmpl = $('#item_template').html()
    $.get( "/get_resources", (data) => {
      for (var i in data) {
        console.log(data[i])
        addItem(container, tmpl, data[i])
      }
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
