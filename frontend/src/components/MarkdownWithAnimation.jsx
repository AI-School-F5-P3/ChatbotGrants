import React from 'react';
import Typewriter from 'typewriter-effect';

function MiComponente() {
  return (
    <Typewriter
      options={{
        strings: ['<strong>Hola</strong>', '<em>Mundo</em>'],
        autoStart: true,
        loop: false, // Establece loop en false para que no repita el efecto
        deleteSpeed: 0, // Establece deleteSpeed en 0 para que no borre el texto
      }}
    />
  );
}

export default MiComponente;
