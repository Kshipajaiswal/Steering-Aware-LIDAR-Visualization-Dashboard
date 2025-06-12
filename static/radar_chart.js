const ctx = document.getElementById('radarChart').getContext('2d');

// Plugin to draw concentric circles and crosshairs
Chart.register({
    id: 'radarOverlay',
    beforeDraw(chart) {
        const { ctx, chartArea: { top, bottom, left, right }, scales } = chart;
        const centerX = scales.x.getPixelForValue(0);
        const centerY = scales.y.getPixelForValue(0);
        const radiusSteps = [2000, 4000, 6000, 8000, 10000];

        ctx.save();
        ctx.strokeStyle = '#ddd';
        ctx.lineWidth = 1;

        // Draw concentric circles
        radiusSteps.forEach(r => {
            const pixelRadius = Math.abs(scales.x.getPixelForValue(r) - centerX);
            ctx.beginPath();
            ctx.arc(centerX, centerY, pixelRadius, 0, 2 * Math.PI);
            ctx.stroke();
        });

        // Draw cross lines
        ctx.beginPath();
        ctx.moveTo(centerX, top);
        ctx.lineTo(centerX, bottom);
        ctx.moveTo(left, centerY);
        ctx.lineTo(right, centerY);
        ctx.stroke();
        ctx.restore();
    }
});

const radarChart = new Chart(ctx, {
    type: 'scatter',
    data: {
        datasets: [{
            label: 'Scan Points',
            data: [],
            pointBackgroundColor: 'rgba(0, 255, 0, 0.8)',
            parsing: false
        }]
    },
    options: {
        responsive: true,
        animation: false,
        maintainAspectRatio: true,
        scales: {
            x: {
                type: 'linear',
                min: -8000,
                max: 8000,
                grid: {
                    color: ctx => (ctx.tick.value === 0 ? '#000' : '#ccc'),
                    lineWidth: ctx => (ctx.tick.value === 0 ? 2 : 1)
                },
                ticks: {
                    font: { size: 14 },
                    stepSize: 1000
                }
            },
            y: {
                type: 'linear',
                min: -8000,
                max: 8000,
                grid: {
                    color: ctx => (ctx.tick.value === 0 ? '#000' : '#ccc'),
                    lineWidth: ctx => (ctx.tick.value === 0 ? 2 : 1)
                },
                ticks: {
                    font: { size: 14 },
                    stepSize: 2000
                }
            }
        },
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: ctx => {
                        const angle = ctx.raw.angleDeg.toFixed(1);
                        const distanceM = (ctx.raw.distance / 1000).toFixed(1);
                        return `Angle: ${angle}°, Distance: ${distanceM} m`;
                    }
                }
            }
        },
        elements: {
            point: {
                radius: ctx => ctx.raw?.r ?? 5
            }
        }
    }
});

function updateData() {
    fetch('/get_scan_data')
        .then(res => res.json())
        .then(points => {
            if (!Array.isArray(points) || points.length === 0) {
                console.error('Invalid data received');
                return;
            }

            // Filter and convert polar to cartesian
            const cartesianPoints = points
                .filter(([angle, distance]) => distance > 0)
                .map(([angleDeg, distance, intensity]) => {
                    const angleRad = angleDeg * Math.PI / 180;
                    return {
                        x: distance * Math.cos(angleRad),
                        y: distance * Math.sin(angleRad),
                        angleDeg,
                        distance,
                        r: Math.max(2, Math.min(8, intensity / 20))  // Scale radius
                    };
                });

            // Update radar chart
            radarChart.data.datasets[0].data = cartesianPoints;
            radarChart.update();

            // Update data table efficiently
            const tbody = document.querySelector('#data-table tbody');
            const rows = points.map(([a, d, i]) =>
                `<tr><td>${a.toFixed(2)}</td><td>${d}</td><td>${i}</td></tr>`
            ).join('');
            tbody.innerHTML = rows;

            // Update steering angle
            fetch('/get_car_steering_angle')
                .then(res => res.json())
                .then(data => {
                    const newSteeringAngle = data.steering_angle;
                    updateCarSteering(newSteeringAngle);
                })
                .catch(err => console.error('Error fetching steering angle:', err));

        })
        .catch(err => {
            console.error('Error fetching data:', err);
        });
}

function updateCarSteering(angle) {
    const car = document.getElementById("car");
    const angleDisplay = document.getElementById("steering-angle-display");
    car.style.transform = `rotate(${angle}deg)`;
    angleDisplay.textContent = `Steering Angle: ${angle.toFixed(1)}°`;
}



function decideSteeringAngle(points, safeDistance = 1000) {
    const front = points.filter(([angle, dist]) => (angle >= -10 || angle <= 10) && dist < safeDistance);
    const right = points.filter(([angle, dist]) => angle >= 40 && angle <= 50 && dist < safeDistance);
    const left  = points.filter(([angle, dist]) => angle >= 310 && angle <= 320 && dist < safeDistance);

    if (front.length > 0) {
        if (left.length > 0 && right.length > 0) {
            return 0; // Stop or hold
        } else if (left.length > 0) {
            return 45; // Turn right
        } else if (right.length > 0) {
            return -45; // Turn left
        } else {
            return -30; // Slight left by default
        }
    }

    return 0; // Path is clear
}


// Fetch data every 500ms
setInterval(updateData, 500);
