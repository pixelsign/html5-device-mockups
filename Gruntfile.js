module.exports = function (grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                files: {
                    'dist/device-mockups.css': 'src/less/device-mockups.scss'
                }
            }
        },
        cssmin: {
            target: {
                files: {
                    'dist/device-mockups.min.css': ['dist/device-mockups.css']
                }
            }
        },
        usebanner: {
            taskName: {
                options: {
                    position: 'top',
                    banner: '/*!\n * <%= pkg.name %> (<%= pkg.link %>)\n * Copyright 2013 - <%= grunt.template.today("yyyy") %> pixelsign\n * Licensed under MIT (https://github.com/pixelsign/html5-device-mockups/blob/master/LICENSE.txt)\n * Last Build: <%= grunt.template.today() %>\n */',
                    linebreak: true
                },
                files: {
                    src: ['dist/device-mockups.css']
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-banner');
    grunt.loadNpmTasks('grunt-sass');

    grunt.registerTask('default', ['sass', 'cssmin', 'usebanner']);

};
