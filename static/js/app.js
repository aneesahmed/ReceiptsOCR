// static/js/app.js

new Vue({
    el: '#app',
    data: {
        selectedFile: null,
        imageUrl: null,
        isLoading: false,
        coordinates: null,
        cropperInstance: null,
        croppedData: null,
        // Mock response data
        mockApiCoordinates: {
            "filename": "invoice7.jpeg",
            "output_filename": "invoice7_cropped.jpeg",
            "x": 1125,
            "y": 993,
            "w": 1899,
            "h": 2291,
            "status": "Cropped and Coordinates Found"
        }
    },
    methods: {
        // --- Step 1: Handle File Selection ---
        onFileChange(e) {
            const file = e.target.files[0];
            if (file) {
                this.selectedFile = file;
                this.imageUrl = URL.createObjectURL(file);
                this.coordinates = null;
                this.croppedData = null;
                this.destroyCropper();
            }
        },

        // --- Step 2: Submit Image for Coordinates (MOCK API) ---
        submitImageForCoordinates() {
            if (!this.selectedFile) return;

            this.isLoading = true;
            this.coordinates = null;
            this.croppedData = null;
            this.destroyCropper();

            // --- MOCK API CALL SIMULATION ---
            console.log('Simulating API call to submit image:', this.selectedFile.name);
            setTimeout(() => {
                this.isLoading = false;
                this.coordinates = this.mockApiCoordinates;
                console.log('Mock API Response:', this.coordinates);
                // Initialization is now manual (via button click)
            }, 1500);
        },

        // --- Initialize Cropper.js (Triggered by button) ---
        initCropper() {
            if (!this.coordinates) return;

            const imageElement = this.$refs.image;
            if (!imageElement) {
                console.error("Image element not found for Cropper.js initialization.");
                return;
            }

            const setupCropper = () => {
                if (this.cropperInstance) return;

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

        // --- Step 3: Submit Final Cropped Data (MOCK API) ---
        submitCroppedImage() {
            if (!this.cropperInstance) {
                alert('Please initialize the cropper first!');
                return;
            }

            this.isLoading = true;

            const cropData = this.cropperInstance.getData(true);

            // --- MOCK API CALL SIMULATION ---
            const submissionPayload = {
                ...cropData,
                originalFileName: this.selectedFile.name,
                targetEndpoint: 'final_crop_submission_endpoint'
            };

            console.log('Simulating API call to submit final crop:', submissionPayload);
            setTimeout(() => {
                this.isLoading = false;
                this.croppedData = submissionPayload;
                alert('Final cropped data simulated to be submitted!');
            }, 1500);
        }
    },
    beforeDestroy() {
        this.destroyCropper();
    }
});