print('''{
  "((1, 0), 'x_(0, 0)', 'in')": false,
  "((1, 0), 'x_(0, 0)', 'out')": false,
  "((1, 0), 'y_(0, 1)', 'in')": true,
  "((1, 0), 'y_(0, 1)', 'out')": false,
  "((1, 0), 'z_(0, 2)', 'in')": false,
  "((1, 0), 'z_(0, 2)', 'out')": false,
  "((1, 1), 'x_(0, 0)', 'in')": false,
  "((1, 1), 'x_(0, 0)', 'out')": false,
  "((1, 1), 'y_(0, 1)', 'in')": false,
  "((1, 1), 'y_(0, 1)', 'out')": false,
  "((1, 1), 'z_(0, 2)', 'in')": true,
  "((1, 1), 'z_(0, 2)', 'out')": false,
  "((1, 2), 'x_(0, 0)', 'in')": true,
  "((1, 2), 'x_(0, 0)', 'out')": false,
  "((1, 2), 'y_(0, 1)', 'in')": false,
  "((1, 2), 'y_(0, 1)', 'out')": false,
  "((1, 2), 'z_(0, 2)', 'in')": false,
  "((1, 2), 'z_(0, 2)', 'out')": false
}''' == '''{
  "((1, 0), 'x_(0, 0)', 'in')": false,
  "((1, 0), 'x_(0, 0)', 'out')": false,
  "((1, 0), 'y_(0, 1)', 'in')": true,
  "((1, 0), 'y_(0, 1)', 'out')": false,
  "((1, 0), 'z_(0, 2)', 'in')": false,
  "((1, 0), 'z_(0, 2)', 'out')": false,
  "((1, 1), 'x_(0, 0)', 'in')": false,
  "((1, 1), 'x_(0, 0)', 'out')": false,
  "((1, 1), 'y_(0, 1)', 'in')": false,
  "((1, 1), 'y_(0, 1)', 'out')": false,
  "((1, 1), 'z_(0, 2)', 'in')": true,
  "((1, 1), 'z_(0, 2)', 'out')": false,
  "((1, 2), 'x_(0, 0)', 'in')": true,
  "((1, 2), 'x_(0, 0)', 'out')": false,
  "((1, 2), 'y_(0, 1)', 'in')": false,
  "((1, 2), 'y_(0, 1)', 'out')": false,
  "((1, 2), 'z_(0, 2)', 'in')": false,
  "((1, 2), 'z_(0, 2)', 'out')": false
}''')