class Config:
    SECRET_KEY = "48xjkl592373YW9akuhsiIHdsfersvUGB<A8AD78EawyuvbdxyuvUXH-..IUELI+IWOZ,UJUNO{$5G7"
    DEBUG      =   True

class DevelopmentConfig(Config):
    MYSQL_HOST     = 'localhost'
    MYSQL_USER     = 'root'
    MYSQL_PASSWORD = 'mysql'
    MYSQL_DB       = 'pait'

config = {
    'development' : DevelopmentConfig
}