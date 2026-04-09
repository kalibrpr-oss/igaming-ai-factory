/** Статический export Next: динамический сегмент [id] запрещён — карточка через query. */
export function adminUserDetailPath(id: number): string {
  return `/admin/users/detail?id=${id}`;
}
