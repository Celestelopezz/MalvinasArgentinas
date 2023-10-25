//Menu
const nav = document.querySelector("#nav");
const abrir = document.querySelector("#abrir-menu");
const cerrar = document.querySelector("#cerrar-menu");

abrir.addEventListener("click", () => {
    nav.classList.add("visible");
})

cerrar.addEventListener("click", () => {
    nav.classList.remove("visible");
})
//FIN Menu

//Mapa
function initMap() {
    var geocoder = new google.maps.Geocoder();
    var direccion = "DMF, Av. 12 de Octubre 1168, B1828 Villa Centenario, Provincia de Buenos Aires";
    var mapa = new google.maps.Map(document.getElementById('mapa'), {
      zoom: 15 // Nivel de zoom
    });

    geocoder.geocode({'address': direccion}, function(results, status) {
      if (status === 'OK') {
        mapa.setCenter(results[0].geometry.location); // Centra el mapa en las coordenadas del lugar
        var marcador = new google.maps.Marker({
          map: mapa,
          position: results[0].geometry.location,
          title: direccion // Nombre del lugar que se mostrará al hacer clic en el marcador
        });
      } else {
        alert('La geocodificación no pudo ser completada debido a: ' + status);
      }
    });
  }
  //FIN Mapa

  //FORMULARIO

