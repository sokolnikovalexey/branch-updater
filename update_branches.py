from subprocess import check_call
from subprocess import CalledProcessError

class Logger:
	def __init__(self, log_file):
		self.log_file = log_file

	def log(self, message):
		if self.log_file is not None:
			self.log_file.write(message + '\n')
			self.log_file.flush()
		print message

class BranchUpdater:
    def __init__(self, branches, up_to_date_branch, check_task, logger):
        self.branches = branches
        self.up_to_date_branch = up_to_date_branch
        self.check_task = check_task
        self.logger = logger
        self.failedList = []
        self.successList = []

    def update(self, branch):
        try:
            check_call(['git', 'fetch', '--all'])
            check_call(['git', 'checkout', branch])
            check_call(['git', 'merge', self.up_to_date_branch])
            check_call('gulp ' + self.check_task, shell=True)
            check_call(['git', 'push'])         
        except CalledProcessError as e:
            logger.log('Error: ' + branch + ' update failed. Reverting...')
            self.failedList.append(branch)
            logger.log(str(e))
            check_call(['git', 'reset', '--hard', '@{u}'])
        else:
             self.successList.append(branch)
 
    def stat(self):
        successedCount = len(self.successList)
        failedCount = len(self.failedList)
        logger.log('==Stat==')
        logger.log('Total: ' + str(successedCount + failedCount) + ', Success: ' + str(successedCount) + ', Fail: ' + str(failedCount))
        logger.log('Updated: ')
        for b in self.successList: logger.log('* ' + b)
        logger.log('Failed: ')
        for b in self.failedList: logger.log('* ' + b)
        logger.log('====')

#Let the magic begin!
branches = ['', '']
up_to_date_branch = ''
check_task = ''
log_file = open('update_log.txt', 'w')

logger = Logger(log_file)
updater = BranchUpdater(branches, up_to_date_branch, check_task, logger)

for branch in branches:
    updater.update(branch)
updater.stat()