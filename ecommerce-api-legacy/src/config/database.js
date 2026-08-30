const sqlite3 = require('sqlite3');

const { config } = require('./index');

/**
 * Wrapper Promise-based sobre o driver `sqlite3`, que só expõe callbacks.
 *
 * Existe para dois motivos:
 *  1. Permitir `async/await` nas camadas superiores (elimina o callback hell).
 *  2. Oferecer `transaction()` com commit/rollback — o código legado gravava
 *     matrícula, pagamento e auditoria sem transação, deixando registros órfãos
 *     quando um dos passos falhava.
 */
class Database {
    constructor(filename = config.database.file) {
        this.filename = filename;
        this.db = null;
        // SQLite aceita uma transação por conexão. Como usamos conexão única,
        // esta fila serializa as transações para que não se sobreponham.
        this.transactionQueue = Promise.resolve();
    }

    connect() {
        return new Promise((resolve, reject) => {
            this.db = new sqlite3.Database(this.filename, (err) => {
                if (err) return reject(err);
                // Sem este PRAGMA o SQLite ignora as FOREIGN KEYs declaradas.
                this.db.run('PRAGMA foreign_keys = ON', (pragmaErr) =>
                    pragmaErr ? reject(pragmaErr) : resolve(this)
                );
            });
        });
    }

    /** Executa INSERT/UPDATE/DELETE. Retorna `{ lastID, changes }`. */
    run(sql, params = []) {
        return new Promise((resolve, reject) => {
            // function() (não arrow) para acessar `this.lastID` do driver.
            this.db.run(sql, params, function callback(err) {
                if (err) return reject(err);
                resolve({ lastID: this.lastID, changes: this.changes });
            });
        });
    }

    /** Retorna a primeira linha, ou `undefined`. */
    get(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.get(sql, params, (err, row) => (err ? reject(err) : resolve(row)));
        });
    }

    /** Retorna todas as linhas. */
    all(sql, params = []) {
        return new Promise((resolve, reject) => {
            this.db.all(sql, params, (err, rows) => (err ? reject(err) : resolve(rows || [])));
        });
    }

    /** Executa múltiplos statements (DDL, seeds). */
    exec(sql) {
        return new Promise((resolve, reject) => {
            this.db.exec(sql, (err) => (err ? reject(err) : resolve()));
        });
    }

    /**
     * Executa `work` dentro de uma transação, com rollback automático em caso
     * de erro. `work` recebe esta mesma instância para encadear as queries.
     */
    transaction(work) {
        const run = async () => {
            await this.run('BEGIN IMMEDIATE TRANSACTION');
            try {
                const result = await work(this);
                await this.run('COMMIT');
                return result;
            } catch (err) {
                await this.run('ROLLBACK').catch(() => {
                    /* preserva o erro original */
                });
                throw err;
            }
        };

        // Encadeia na fila e devolve o resultado desta execução específica.
        const queued = this.transactionQueue.then(run, run);
        this.transactionQueue = queued.catch(() => {});
        return queued;
    }

    close() {
        return new Promise((resolve, reject) => {
            if (!this.db) return resolve();
            this.db.close((err) => (err ? reject(err) : resolve()));
        });
    }
}

module.exports = Database;
