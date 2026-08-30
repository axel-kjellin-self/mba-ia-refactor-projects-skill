const { config, validate } = require('./src/config');
const Database = require('./src/config/database');
const { createTables, seed } = require('./src/models/schema');
const createApp = require('./src/app');
const logger = require('./src/utils/logger');

/**
 * Entry point: valida a configuração, prepara o banco, sobe o servidor e
 * trata o encerramento gracioso.
 */
async function main() {
    validate();

    const db = await new Database().connect();
    await createTables(db);
    await seed(db);

    const app = createApp({ db });

    const server = app.listen(config.port, () => {
        logger.info('Servidor iniciado', { port: config.port, env: config.env });
    });

    const shutdown = async (signal) => {
        logger.info('Encerrando servidor', { signal });
        server.close(async () => {
            await db.close().catch((err) =>
                logger.error('Falha ao fechar o banco', { message: err.message })
            );
            process.exit(0);
        });
    };

    process.on('SIGINT', () => shutdown('SIGINT'));
    process.on('SIGTERM', () => shutdown('SIGTERM'));
}

main().catch((err) => {
    logger.error('Falha ao iniciar a aplicação', { message: err.message, stack: err.stack });
    process.exit(1);
});
