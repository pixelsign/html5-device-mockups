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
        },
        cssmin: {
            target: {
                files: {
                    'dist/main.min.css': ['src/main.css']
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('default', ['less', 'cssmin']);

};
