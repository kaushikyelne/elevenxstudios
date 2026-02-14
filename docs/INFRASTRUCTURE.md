# Cloud Infrastructure & Deployment

MoneyLane is deployed as a modern, cloud-native application on Google Cloud Platform (GCP).

## Production Architecture

- **Compute**: [GCP Cloud Run](https://cloud.google.com/run) (Serverless, auto-scaling)
- **Database**: [GCP Cloud SQL](https://cloud.google.com/sql) (Managed PostgreSQL with Private IP)
- **Security**: 
    - [GCP Secret Manager](https://cloud.google.com/secret-manager) for sensitive configuration.
    - Custom Service Account with Least Privilege.
- **Networking**:
    - **Domain**: `api.moneylane.elevenxstudios.com`
    - **Swagger UI**: [https://api.moneylane.elevenxstudios.com/swagger-ui/index.html](https://api.moneylane.elevenxstudios.com/swagger-ui/index.html)
    - **SSL/TLS**: Automatic provisioning via GCP.
    - **Ingress**: Configured for public access with restricted internal paths.

## Key Learnings & Milestones

1.  **Serverless Deployment**: Successfully containerized and deployed Spring Boot to Cloud Run.
2.  **Private Networking**: Connected backend to Cloud SQL securely via private IP and socket factory.
3.  **Cross-Architecture Builds**: Solved Docker `ARM64` (Mac) vs `AMD64` (Cloud) compatibility issues using multi-stage builds and explicit platform flags.
4.  **Configuration Safety**: Moved from hardcoded environment variables to Secret Manager.
5.  **Domain Management**: Verified ownership via Search Console and configured DNS (CNAME/TXT) in Namecheap.
6.  **TLS Lifecycle**: Debugged handshake issues and verified automatic SSL certificate provisioning.
7.  **Transition**: Successfully moved from `docker-compose` local development to a production-ready cloud architecture.

---

*This infrastructure represents a shift from local-first development to a scalable, secure, and professional cloud-native application.*
