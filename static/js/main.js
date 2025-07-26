
function createParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.classList.add('particle');
        
      
        const size = Math.random() * 5 + 2;
        particle.style.width = `${size}px`;
        particle.style.height = `${size}px`;
        
        
        particle.style.left = `${Math.random() * 100}vw`;
        particle.style.top = `${Math.random() * 100}vh`;
        
        const duration = Math.random() * 20 + 10;
        particle.style.animationDuration = `${duration}s`;
        
       
        particle.style.animationDelay = `${Math.random() * 5}s`;
        
        particlesContainer.appendChild(particle);
    }
}

function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('imagen');
    const fileName = document.getElementById('file-name');
    const predictBtn = document.getElementById('predict-btn');
    
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileName.textContent = `Archivo seleccionado: ${e.target.files[0].name}`;
            predictBtn.disabled = false;
        } else {
            fileName.textContent = '';
            predictBtn.disabled = true;
        }
    });
}


async function enviar() {
    const input = document.getElementById('imagen');
    const resultContainer = document.getElementById('result-container');
    const resultado = document.getElementById('resultado');
    const confidence = document.getElementById('confidence');
    
    if (input.files.length === 0) {
        alert('Por favor selecciona una imagen primero');
        return;
    }
    
  
    resultado.textContent = "Analizando imagen...";
    confidence.textContent = "";
    resultContainer.style.display = "block";
    
    const formData = new FormData();
    formData.append('imagen', input.files[0]);

    try {
        const res = await fetch('/prediccion', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error('Error en la solicitud');
        
        const data = await res.json();
        resultado.textContent = "Resultado: " + data.resultado;
        
       
        
    } catch (error) {
        console.error('Error:', error);
        resultado.textContent = "Error al procesar la imagen";
        confidence.textContent = "";
    }
}


document.addEventListener('DOMContentLoaded', () => {
    createParticles();
    setupFileUpload();
    
    document.getElementById('predict-btn').addEventListener('click', enviar);
  
    const fadeElements = document.querySelectorAll('.fade-in');
    
    const fadeInOnScroll = () => {
        fadeElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementTop < windowHeight - 100) {
                element.style.opacity = "1";
                element.style.transform = "translateY(0)";
            }
        });
    };
    
 
    fadeInOnScroll();
    window.addEventListener('scroll', fadeInOnScroll);
});