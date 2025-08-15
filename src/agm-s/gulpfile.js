
const gulp = require('gulp');

const sass = require('gulp-sass')(require('sass'));

gulp.task('css', function () {
    return gulp.src('./asset/sass/*.scss')
        .pipe(sass({
            outputStyle: "expanded",
            includePaths: ['node_modules/susy/sass'],
            })
        )
        .pipe(gulp.dest('./asset/css'));
});
