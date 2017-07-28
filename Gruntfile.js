module.exports = function (grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        less: {
            development: {
                options: {
                    plugins: [
                        new (require('less-plugin-autoprefix'))({browsers: ["last 2 versions"]})
                    ],
                },
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

    grunt.registerTask('default', ['less', 'cssmin', 'usebanner']);

};