module.exports = function(grunt) {

    grunt.initConfig({
        less: {
            development: {
                options: {
                    paths: ['src']
                },
                files: {
                    'src/main.css': 'src/main.less'
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');

    grunt.registerTask('default', ['less']);

};
