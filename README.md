# 🎬 MovieMatch - Tu Asistente Personal de Películas

![MovieMatch](https://img.shields.io/badge/MovieMatch-v1.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8+-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![TMDB](https://img.shields.io/badge/TMDB-API-yellow.svg)

MovieMatch es una aplicación web interactiva desarrollada con Streamlit que te ayuda a descubrir películas perfectas usando la poderosa API de The Movie Database (TMDB). Con un sistema de recomendaciones inteligente y una interfaz amigable, encontrar tu próxima película favorita nunca fue tan fácil.

## ✨ Características Principales

### 🔍 Búsqueda Avanzada
- **Búsqueda por título**: Encuentra películas específicas por nombre
- **Resultados detallados**: Información completa con posters, sinopsis, puntuaciones y más
- **Filtros inteligentes**: Busca por año, género, puntuación mínima

### 🎯 Sistema de Recomendaciones IA
- **Basado en películas**: Encuentra películas similares a las que te gustaron
- **Basado en géneros**: Descubre contenido por tus géneros favoritos  
- **Perfil personalizado**: Crea tu perfil de preferencias para recomendaciones únicas
- **Mezcla aleatoria**: Sorpréndete con combinaciones personalizadas

### 📊 Exploración de Contenido
- **Películas populares**: Las más vistas del momento
- **Mejor valoradas**: Clásicos y joyas cinematográficas
- **En cines**: Estrenos actuales en cartelera
- **Próximos estrenos**: Mantente al día con los lanzamientos

### 🎬 Información Detallada
- **Detalles completos**: Duración, presupuesto, recaudación, productoras
- **Trailers integrados**: Ve trailers directamente en la aplicación
- **Películas relacionadas**: Descubre contenido similar automáticamente
- **Géneros y clasificaciones**: Información completa de categorización

## 🚀 Instalación y Configuración

### Prerrequisitos
- Python 3.8 o superior
- Cuenta en [The Movie Database (TMDB)](https://www.themoviedb.org/)
- API Key de TMDB (gratuita)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/MovieMatch.git
cd MovieMatch
```

### 2. Crear Entorno Virtual (Recomendado)
```bash
python -m venv moviematch_env

# En Windows
moviematch_env\Scripts\activate

# En macOS/Linux
source moviematch_env/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar API Key de TMDB

#### Obtener tu API Key:
1. Regístrate en [TMDB](https://www.themoviedb.org/signup)
2. Ve a tu perfil → Configuración → API
3. Solicita una API Key (es gratuita y se aprueba inmediatamente)

#### Configurar la clave:
Crea un archivo `.env` en el directorio raíz del proyecto:

```env
TMDB_API_KEY=tu_api_key_aqui
```

**¡Importante!** Nunca compartas tu API key públicamente ni la subas a repositorios.

### 5. Ejecutar la Aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

## 📱 Guía de Uso

### Navegación Principal
La aplicación cuenta con 7 secciones principales accesibles desde la barra lateral:

1. **🔍 Buscar Películas**
   - Ingresa el nombre de cualquier película
   - Explora resultados con información detallada
   - Haz clic en "Ver más detalles" para información completa

2. **🔥 Películas Populares**
   - Descubre las películas más populares del momento
   - Actualizado automáticamente según las tendencias de TMDB

3. **🏆 Mejor Valoradas**
   - Explora películas con las mejores puntuaciones
   - Clásicos y joyas cinematográficas reconocidas

4. **🎪 En Cines**
   - Películas actualmente en cartelera
   - Mantente al día con los estrenos actuales

5. **🗓️ Próximos Estrenos**
   - Próximas películas a estrenar
   - Planifica tus próximas visitas al cine

6. **🎯 Descubrir**
   - Usa filtros avanzados para encontrar películas específicas
   - Filtra por género, año, puntuación mínima
   - Ordena resultados según tus preferencias

7. **🤖 Recomendaciones IA**
   - Sistema inteligente de recomendaciones
   - 4 métodos diferentes de recomendación
   - Personalización avanzada según tus gustos

### Sistema de Recomendaciones Detallado

#### 🎬 Basado en Películas
1. Busca una película que te haya gustado
2. Selecciónala de los resultados
3. Obtén películas similares y recomendaciones automáticas

#### 🎭 Basado en Géneros
1. Selecciona tus géneros favoritos
2. Ajusta filtros de año y puntuación
3. Descubre películas que coincidan con tus gustos

#### 👤 Perfil Personalizado
1. Completa el formulario de preferencias
2. Selecciona géneros, década preferida, duración
3. Recibe recomendaciones completamente personalizadas

#### 🔀 Mezcla Aleatoria
1. Elige el tipo de mezcla que prefieres
2. Obtén una combinación sorprendente de películas
3. Perfecta para cuando no sabes qué ver

## 🛠️ Estructura del Proyecto

```
MovieMatch/
│
├── app.py                 # Aplicación principal de Streamlit
├── utils.py              # Cliente TMDB y funciones auxiliares
├── recommendations.py    # Sistema de recomendaciones avanzado
├── requirements.txt      # Dependencias de Python
├── .env                 # Variables de entorno (crear manualmente)
├── README.md            # Documentación del proyecto
└── .gitignore          # Archivos ignorados por Git
```

## 🔧 Tecnologías Utilizadas

- **[Streamlit](https://streamlit.io/)**: Framework web para aplicaciones de datos
- **[TMDB API](https://developers.themoviedb.org/3)**: Base de datos de películas
- **[Requests](https://requests.readthedocs.io/)**: Cliente HTTP para Python
- **[Python-dotenv](https://pypi.org/project/python-dotenv/)**: Gestión de variables de entorno
- **[Pandas](https://pandas.pydata.org/)**: Manipulación de datos (para futuras mejoras)

## 🎨 Características de la Interfaz

- **Diseño Responsivo**: Funciona perfectamente en desktop y móvil
- **Tarjetas Interactivas**: Información organizada en tarjetas visuales
- **Imágenes Optimizadas**: Posters y fondos en alta calidad
- **Navegación Intuitiva**: Barra lateral para acceso rápido
- **Feedback Visual**: Spinners y mensajes de estado
- **Estilo Personalizado**: CSS integrado para mejor experiencia

## 🤝 Contribuir al Proyecto

¡Las contribuciones son bienvenidas! Si quieres mejorar MovieMatch:

1. **Fork** el repositorio
2. Crea una **rama feature** (`git checkout -b feature/nueva-caracteristica`)
3. **Commit** tus cambios (`git commit -m 'Añadir nueva característica'`)
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un **Pull Request**

### Ideas para Contribuir
- [ ] Agregar soporte para series de TV
- [ ] Implementar sistema de favoritos local
- [ ] Añadir más proveedores de streaming
- [ ] Mejorar algoritmos de recomendación
- [ ] Implementar modo oscuro
- [ ] Añadir internacionalización (i18n)

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

## 🙏 Reconocimientos

- **[The Movie Database (TMDB)](https://www.themoviedb.org/)** por proporcionar la API gratuita
- **[Streamlit](https://streamlit.io/)** por el excelente framework web
- **Comunidad de desarrolladores** por el feedback y contribuciones

## 📞 Soporte y Contacto

Si tienes preguntas, sugerencias o encuentras algún problema:

- 🐛 **Reportar bugs**: [Abrir un issue](https://github.com/tu-usuario/MovieMatch/issues)
- 💡 **Sugerir mejoras**: [Discusiones](https://github.com/tu-usuario/MovieMatch/discussions)
- 📧 **Contacto directo**: tu-email@ejemplo.com

## 🚀 Versiones Futuras

### v1.1 (Próximamente)
- [ ] Sistema de favoritos persistente
- [ ] Exportar listas de películas
- [ ] Integración con plataformas de streaming

### v1.2 (En planificación)
- [ ] Soporte para series de TV
- [ ] Modo oscuro
- [ ] Aplicación móvil nativa

---

**¡Disfruta descubriendo tu próxima película favorita con MovieMatch! 🍿🎬**