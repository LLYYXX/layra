// 将身份验证切换到admin数据库
db = db.getSiblingDB('admin');

// 创建管理员用户
db.createUser({
  user: 'mongouser',
  pwd: 'mongo577715',
  roles: [
    { role: 'readWriteAnyDatabase', db: 'admin' },
    { role: 'userAdminAnyDatabase', db: 'admin' },
    { role: 'dbAdminAnyDatabase', db: 'admin' }
  ]
});

// 切换到目标数据库
db = db.getSiblingDB('mongodb');

// 创建必要的集合
db.createCollection('model_config');
db.createCollection('conversations');
db.createCollection('knowledge_bases');
db.createCollection('files');

// 创建索引（如有需要）
db.model_config.createIndex({ "username": 1 }, { unique: true });
db.conversations.createIndex({ "conversation_id": 1 }, { unique: true });
db.knowledge_bases.createIndex({ "knowledge_base_id": 1 }, { unique: true });
db.files.createIndex({ "file_id": 1 }, { unique: true });

print('MongoDB初始化完成'); 