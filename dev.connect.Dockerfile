FROM mkeller7/conda-starlette:python3.7

# Starlette environment variables
ENV PORT 8200
ENV DEBUG '1'
# Force usage of single worker to deal with websockets
ENV WEB_CONCURRENCY '1'