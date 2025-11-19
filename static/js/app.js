// static/js/app.js

// Retrieve the base URL from the global object injected by the FastAPI server.
const BASE_URL = window.API_CONFIG ? window.API_CONFIG.BASE_URL : 'http://localhost:8000'; 

new Vue({
    el: '#app',
    data: {
        selectedFile: null,
        imageUrl: null,
        isLoading: false,
        coordinates: null,
        cropperInstance: null,
        // The final submission data fields are removed
    },
    methods: {
        // --- Step 1: Handle File Selection ---
        onFileChange(e) {
            const file = e.target.files[0];
            if (file) {
                this.selectedFile = file;
                this.imageUrl = URL.createObjectURL(file);
                this.coordinates = null;
                this.destroyCropper(); 
            }
        },

        // --- Step 2: Submit Image for Processing (Manual API Call) ---
        async submitImageForCoordinates() {
            if (!this.selectedFile) return;

            this.isLoading = true;
            this.coordinates = null;
            this.destroyCropper();

            // Prepare the form data to send the file
            const formData = new FormData();
            formData.append('file', this.selectedFile);

            console.log('Sending image to API for saving and processing...');

            try {
                // Use the consolidated endpoint
                const response = await fetch(`${BASE_URL}/api/process_image/`, {
                    method: 'POST',
                    body: formData,
                });

                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(`HTTP error! Status: ${response.status}. Details: ${errorText}`);
                }

                const data = await response.json();
                
                this.isLoading = false;
                // Basic check for coordinate data validity
                if (data && data.x !== undefined) {
                    this.coordinates = data;
                } else {
                    console.error("API returned invalid or missing coordinate data:", data);
                    this.coordinates = null;
                }
                
                console.log('API Response (Coordinates and Status):', this.coordinates);

                // Cropper Initialization now waits for manual button click

            } catch (error) {
                this.isLoading = false;
                this.coordinates = null;
                console.error('Error submitting image:', error);
                alert(`Processing Failed. Check server status and console. Error: ${error.message}`);
            }
        },

        // --- Initialize Cropper.js (Triggered by manual button click) ---
        initCropper() {
            if (!this.coordinates) return;

            const imageElement = this.$refs.image; 
            if (!imageElement) {
                console.error("Image element reference not found.");
                return;
            }
            
            const setupCropper = () => {
                if (this.cropperInstance) return; 

                // Use coordinates from the single API response
                const { x, y, w, h } = this.coordinates;

                this.cropperInstance = new Cropper(imageElement, {
                    aspectRatio: NaN,
                    viewMode: 1, 
                    ready: () => {
                        this.cropperInstance.setData({
                            x: x,
                            y: y,
                            width: w,
                            height: h,
                        });
                        console.log("Cropper initialized and coordinates set.");
                    }
                });
            };

            // Wait for the image element to fully load before initializing
            if (imageElement.complete) {
                setupCropper();
            } else {
                imageElement.onload = setupCropper;
                imageElement.onerror = () => {
                    console.error("Error loading image before initializing Cropper.");
                };
            }
        },

        // --- Clean up the Cropper instance ---
        destroyCropper() {
            if (this.cropperInstance) {
                this.cropperInstance.destroy();
                this.cropperInstance = null;
            }
        },
    },
    beforeDestroy() {
        this.destroyCropper();
    }
});