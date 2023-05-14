FROM php:8.1.19-apache

# Enable mysqli extension
RUN docker-php-ext-install mysqli

COPY ./pages /var/www/html/
