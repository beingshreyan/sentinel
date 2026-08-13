const API_BASE_URL = "https://sentinel-gdnk.onrender.com";


const accessGate =
    document.getElementById("access-gate");

const storeContent =
    document.getElementById("store-content");

const customerForm =
    document.getElementById("customer-form");

const locationButton =
    document.getElementById("location-button");

const locationStatus =
    document.getElementById("location-status");

const formMessage =
    document.getElementById("form-message");

const submitButton =
    document.getElementById("submit-button");



let locationData = {
    latitude: null,
    longitude: null,
    accuracy: null
};


function requestLocation() {

    if (!navigator.geolocation) {

        setMessage(
            "Your browser does not support geolocation.",
            true
        );

        locationStatus.textContent =
            "Geolocation is not supported.";

        return;
    }


    locationStatus.textContent =
        "Requesting location permission...";

    locationButton.disabled = true;

    navigator.geolocation.getCurrentPosition(

        (position) => {

            locationData.latitude =
                position.coords.latitude;

            locationData.longitude =
                position.coords.longitude;

            locationData.accuracy =
                position.coords.accuracy;


            locationStatus.textContent =
                `Location received. Accuracy: ${
                    Math.round(
                        position.coords.accuracy
                    )
                } m`;


            locationButton.textContent =
                "Location Granted";


            locationButton.classList.add(
                "granted"
            );

            locationButton.disabled = false;


            setMessage(
                "Location permission granted.",
                false
            );
        },


        (error) => {

            console.error(
                "Geolocation error:",
                error
            );


            locationButton.disabled = false;


            locationButton.textContent =
                "Allow Location";


            switch (error.code) {

                case error.PERMISSION_DENIED:

                    locationStatus.textContent =
                        "Location permission was denied.";

                    setMessage(
                        "Location permission is required to continue.",
                        true
                    );

                    break;


                case error.POSITION_UNAVAILABLE:

                    locationStatus.textContent =
                        "Location is currently unavailable.";

                    setMessage(
                        "Unable to determine your location.",
                        true
                    );

                    break;


                case error.TIMEOUT:

                    locationStatus.textContent =
                        "Location request timed out.";

                    setMessage(
                        "Location request timed out. Please try again.",
                        true
                    );

                    break;


                default:

                    locationStatus.textContent =
                        "Unable to obtain location.";

                    setMessage(
                        "Unable to obtain your location.",
                        true
                    );
            }
        },


        {
            enableHighAccuracy: true,
            timeout: 10000,
            maximumAge: 0
        }
    );
}


locationButton.addEventListener(
    "click",
    requestLocation
);


customerForm.addEventListener(
    "submit",
    async (event) => {

        event.preventDefault();


        const name =
            document
                .getElementById("name")
                .value
                .trim();


        const email =
            document
                .getElementById("email")
                .value
                .trim();


        const phone =
            document
                .getElementById("phone")
                .value
                .trim();


        if (!name || !email || !phone) {

            setMessage(
                "Please complete all required fields.",
                true
            );

            return;
        }


        if (
            locationData.latitude === null ||
            locationData.longitude === null
        ) {

            setMessage(
                "Please allow location access before continuing.",
                true
            );

            return;
        }


        submitButton.disabled = true;

        submitButton.textContent =
            "Submitting...";


        setMessage(
            "Submitting your information...",
            false
        );


        const browser =
            navigator.userAgent || "";


        const os =
            navigator.platform || "";


        const device =
            navigator.userAgentData?.mobile
                ? "Mobile"
                : "Desktop";


        const payload = {

            name,

            email,

            phone,

            latitude:
                locationData.latitude,

            longitude:
                locationData.longitude,

            accuracy:
                locationData.accuracy,

            browser,

            os,

            device

        };


        try {

            const response =
                await fetch(
                    `${API_BASE_URL}/api/collect`,
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body:
                            JSON.stringify(
                                payload
                            )
                    }
                );


            const result =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    result.detail ||
                    "Submission failed."
                );
            }


            if (!result.success) {

                throw new Error(
                    "The server did not confirm the submission."
                );
            }


            setMessage(
                "Information submitted successfully.",
                false
            );


            accessGate.classList.add(
                "hidden"
            );

            storeContent.classList.remove(
                "hidden"
            );


            document.body.style.overflow =
                "auto";


            window.scrollTo(
                {
                    top: 0,
                    behavior: "instant"
                }
            );


        } catch (error) {

            console.error(
                "Submission error:",
                error
            );


            setMessage(
                error.message ||
                "Unable to submit your information.",
                true
            );


            submitButton.disabled =
                false;

            submitButton.textContent =
                "Continue to Store";
        }
    }
);


function setMessage(
    message,
    isError = false
) {

    formMessage.textContent =
        message;


    formMessage.classList.remove(
        "error",
        "success"
    );


    formMessage.classList.add(
        isError
            ? "error"
            : "success"
    );
}


document.body.style.overflow =
    "hidden";