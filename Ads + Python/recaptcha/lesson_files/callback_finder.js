(token) => {
  function findFirstCallback(obj, currentPath = '', visited = new Set()) {
    // Проверка на null или undefined
    if (obj === null || obj === undefined) {
      return null;
    }
    
    // Проверка на циклические ссылки
    if (typeof obj === 'object' && visited.has(obj)) {
      return null;
    }
    
    // Добавляем текущий объект в список посещенных
    if (typeof obj === 'object') {
      visited.add(obj);
    }
    
    // Если это объект или массив, перебираем его свойства
    if (typeof obj === 'object') {
      for (let key in obj) {
        if (obj.hasOwnProperty(key)) {
          // Если свойство является функцией, проверяем, является ли она callback
          const newPath = currentPath ? `${currentPath}.${key}` : key;
          
          // Проверяем, является ли свойство функцией callback
          if (key === 'callback' && typeof obj[key] === 'function') {
            return {
              path: newPath,
              callback: obj[key]
            };
          }
          
          // Рекурсивно проверяем вложенные объекты
          const result = findFirstCallback(obj[key], newPath, visited);
          if (result) {
            return result;
          }
        }
      }
    }
    return null;
  }

  // Исполняем функцию поиска и выводим результат

  const result = findFirstCallback(___grecaptcha_cfg.clients);
  // Если вы хотите получить доступ к функции для дальнейшего использования
  result.callback(token);
}