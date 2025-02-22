
# @app.middleware("http")
# async def query_caching_middleware(request: Request, call_next):
#     logger.info("hello!")
#     return await call_next(request)
#
# @app.middleware("http")
# async def process_timing_middleware(request: Request, call_next):
#     t0 = datetime.datetime.now()
#     response = await call_next(request)
#     dt = (datetime.datetime.now() - t0)
#     logger.info(f"processing {request.url} took {dt}")
#     return response
#
# @asynccontextmanager
# async def lifespan(_: FastAPI):
#     logger.info("Starting up...")
#     alembic_cfg = Config("alembic.ini")
#     logger.info("run alembic upgrade head...")
#     command.upgrade(alembic_cfg, "head")
#     yield
#     logger.info("Shutting down...")