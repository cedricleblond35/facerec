'use strict';
const util = require('util');
const exec = util.promisify(require('child_process').exec);
const logger = require('../../logger');


/**
 * Class permettant faire des commandes shell
 */
class Execute_command{
    /**
     * Execution d'un commande
     * const exec = util.promisify(require('child_process').exec);
     * @param command_line
     * @returns {Promise<{data: *}>}
     */
    static async execute_command(command_line) {
        const { stdout, stderr } = await exec(command_line, {maxBuffer: 1024 * 1500});

        if (stderr) {
            logger.log({
                level: 'error',
                message: stderr + '\n' + command_line + '\n'
            });
        }
        let stdout2 = stdout.replace(/\n/g, '');

        return {data: stdout2};
    };
}

module.exports = Execute_command;