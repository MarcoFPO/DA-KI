# Entwicklungsrichtlinien für DA-KI

Dieses Dokument beschreibt die grundlegenden Richtlinien und Standards für die Entwicklung des DA-KI-Projekts.

## Übersicht der Planungsdokumente

*   [Technologie-Stack](#1-technologie-stack)
*   [Code-Standards](standards/code_standards.md)
*   [Backend-Kernkomponenten](backend/core_components.md)
*   [Geheimnismanagement](backend/secret_management.md)
*   [Backend-API](backend/api_design.md)
*   [Frontend UI/UX](frontend/ui_ux.md)
*   [Build- und Deployment-Prozess](deployment/build_deploy_process.md)
*   [Entwicklungsumgebung im LXC-Container](deployment/dev_environment.md)
*   [Plugin-Architektur](architecture/plugin_architecture.md)
*   [Dokumentation](general/documentation_guidelines.md)

---

## 1. Technologie-Stack

*   **Backend:** Python
*   **Frontend:** React mit Material-UI (MUI)
*   **Datenbank:** SQLite (lokal im LXC-Container)
*   **Webserver/Reverse Proxy:** Nginx (für externe Kommunikation und TLS-Terminierung)
