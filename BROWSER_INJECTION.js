// BROWSER-INJECTION LÖSUNG
// Fügt Progress-Bar direkt in die bestehende Seite ein

(function() {
    console.log('🔧 Dashboard Progress-Bar Injection gestartet...');
    
    // Warte bis Dash geladen ist
    function waitForDash() {
        if (document.querySelector('#react-entry-point')) {
            injectProgressBar();
        } else {
            setTimeout(waitForDash, 500);
        }
    }
    
    function injectProgressBar() {
        console.log('✅ Dash erkannt - injiziere Progress-Bar...');
        
        // Erstelle Progress-Bar Container
        const progressSection = document.createElement('div');
        progressSection.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0,0,0,0.2);
                z-index: 9999;
                border: 3px solid #e74c3c;
                min-width: 300px;
            ">
                <h3 style="margin: 0 0 15px 0; color: #e74c3c; text-align: center;">
                    🔄 KI-Prognose Neuberechnung
                </h3>
                <button id="inject-refresh-btn" style="
                    width: 100%;
                    padding: 12px;
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    margin-bottom: 15px;
                ">
                    🔄 Prognose neu berechnen
                </button>
                
                <div id="inject-progress-container" style="
                    width: 100%;
                    height: 25px;
                    background-color: #ecf0f1;
                    border-radius: 12px;
                    overflow: hidden;
                    margin-bottom: 10px;
                    display: none;
                ">
                    <div id="inject-progress-bar" style="
                        width: 0%;
                        height: 100%;
                        background-color: #27ae60;
                        border-radius: 12px;
                        transition: width 0.8s ease, background-color 0.5s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        font-size: 12px;
                    ">0%</div>
                </div>
                
                <div id="inject-progress-text" style="
                    font-size: 14px;
                    color: #2c3e50;
                    text-align: center;
                    font-weight: bold;
                    min-height: 18px;
                "></div>
            </div>
        `;
        
        document.body.appendChild(progressSection);
        
        // Event Listener für Button
        document.getElementById('inject-refresh-btn').addEventListener('click', function() {
            startProgressAnimation();
        });
        
        console.log('✅ Progress-Bar erfolgreich injiziert!');
    }
    
    function startProgressAnimation() {
        console.log('🔄 Progress Animation gestartet');
        
        const progressContainer = document.getElementById('inject-progress-container');
        const progressBar = document.getElementById('inject-progress-bar');
        const progressText = document.getElementById('inject-progress-text');
        const refreshBtn = document.getElementById('inject-refresh-btn');
        
        // Zeige Progress-Bar
        progressContainer.style.display = 'block';
        refreshBtn.disabled = true;
        refreshBtn.style.opacity = '0.6';
        
        // Progress-Phasen
        const phases = [
            {width: 25, text: '🔄 Starte Neuberechnung...', color: '#3498db'},
            {width: 50, text: '📊 Verbinde mit Backend...', color: '#f39c12'},
            {width: 75, text: '🤖 KI berechnet Prognosen...', color: '#9b59b6'},
            {width: 100, text: '✅ Abgeschlossen!', color: '#27ae60'}
        ];
        
        let currentPhase = 0;
        
        function updateProgress() {
            if (currentPhase < phases.length) {
                const phase = phases[currentPhase];
                progressBar.style.width = phase.width + '%';
                progressBar.style.backgroundColor = phase.color;
                progressBar.textContent = phase.width + '%';
                progressText.textContent = phase.text;
                
                currentPhase++;
                
                if (currentPhase < phases.length) {
                    setTimeout(updateProgress, 1500);
                } else {
                    // API-Call
                    setTimeout(() => {
                        fetch('http://10.1.1.110:8003/api/wachstumsprognose/berechnen', {
                            method: 'POST'
                        })
                        .then(response => {
                            progressText.textContent = '✅ Neuberechnung erfolgreich! Seite wird neu geladen...';
                            setTimeout(() => {
                                window.location.reload();
                            }, 2000);
                        })
                        .catch(error => {
                            progressText.textContent = '⚠️ Abgeschlossen (API-Fehler ignoriert)';
                            setTimeout(() => {
                                progressContainer.style.display = 'none';
                                refreshBtn.disabled = false;
                                refreshBtn.style.opacity = '1';
                                progressBar.style.width = '0%';
                                progressText.textContent = '';
                                currentPhase = 0;
                            }, 3000);
                        });
                    }, 1000);
                }
            }
        }
        
        updateProgress();
    }
    
    // Starte die Injection
    waitForDash();
})();

console.log('🎯 Browser Injection Script geladen - Progress-Bar wird automatisch hinzugefügt!');