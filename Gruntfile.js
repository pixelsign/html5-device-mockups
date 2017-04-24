module.exports = function(grunt) {

    grunt.initConfig({
        less: {
            development: {
                files: {
                    'dist/device-mockups.css': 'src/device-mockups.less'
                }
            }
        },
        cssmin: {
            target: {
                files: {
                    'dist/device-mockups.min.css': ['dist/device-mockups.css']
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-cssmin');

    grunt.registerTask('default', ['less', 'cssmin']);

};
